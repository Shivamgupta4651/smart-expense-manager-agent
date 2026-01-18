"""
Smart Expense Manager - Android Integration Layer
Kotlin code structure for the Android app using Droidrun framework
"""

# FILE: android/app/src/main/java/com/example/expensemanager/MainActivity.kt

"""
MainActivity.kt - Main Android Application Activity
"""

package com.example.expensemanager

import android.app.NotificationManager
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import android.view.LayoutInflater
import android.widget.Button
import android.widget.EditText
import android.widget.ListView
import android.widget.TextView
import android.widget.ArrayAdapter
import android.widget.Toast
import com.droidrun.framework.DroidrunAgent
import com.droidrun.framework.UIElement
import com.droidrun.framework.NotificationListener
import java.util.*

class MainActivity : AppCompatActivity(), NotificationListener {
    
    private lateinit var agentEngine: ExpenseAgentEngine
    private lateinit var transactionList: ListView
    private lateinit var summaryText: TextView
    private val transactions = mutableListOf<String>()
    private lateinit var adapter: ArrayAdapter<String>
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // Initialize UI components
        transactionList = findViewById(R.id.transaction_list)
        summaryText = findViewById(R.id.summary_text)
        
        // Setup adapter for transaction list
        adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, transactions)
        transactionList.adapter = adapter
        
        // Initialize agent engine
        agentEngine = ExpenseAgentEngine(this)
        
        // Setup Droidrun Agent
        initializeDroidrunAgent()
        
        // Request permissions
        requestRequiredPermissions()
        
        // Setup UI listeners
        setupUIListeners()
    }
    
    private fun initializeDroidrunAgent() {
        try {
            // Initialize Droidrun framework
            DroidrunAgent.initialize(this)
            
            // Register notification listener for payment apps
            DroidrunAgent.registerNotificationListener(this, listOf(
                "com.google.android.apps.nbu.paisa.user",  // Google Pay
                "com.phonepe.app",                          // PhonePe
                "com.paytm",                               // Paytm
                "com.whatsapp"                             // WhatsApp Pay
            ))
            
            // Setup automation tasks
            setupAutomationTasks()
            
        } catch (e: Exception) {
            Toast.makeText(this, "Droidrun initialization failed: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun setupAutomationTasks() {
        // Task 1: Daily summary generation at 9 PM
        agentEngine.scheduleDailyTask(21, 0) {
            generateDailySummary()
        }
        
        // Task 2: Weekly analysis (Every Monday at 8 AM)
        agentEngine.scheduleWeeklyTask(Calendar.MONDAY, 8, 0) {
            generateWeeklySummary()
        }
    }
    
    override fun onNotificationPosted(packageName: String, title: String, text: String) {
        // Called when notification from payment app is detected
        
        // Example: "₹250 to Starbucks Coffee"
        val transactionInfo = text
        
        // Process transaction through agent
        val result = agentEngine.processTransaction(transactionInfo, packageName)
        
        if (result != null) {
            // Add to UI
            val displayText = "${result.category} - ₹${result.amount} (${result.merchant})"
            runOnUiThread {
                transactions.add(0, displayText)
                adapter.notifyDataSetChanged()
                Toast.makeText(
                    this,
                    "✅ ${result.category} recorded",
                    Toast.LENGTH_SHORT
                ).show()
            }
            
            // Check budget
            checkBudgetAlert(result.category, result.amount.toDouble())
        }
    }
    
    private fun checkBudgetAlert(category: String, amount: Double) {
        val budgetStatus = agentEngine.checkBudgetStatus(category)
        
        if (budgetStatus.isAlertNeeded) {
            val alertMessage = when {
                budgetStatus.percentageUsed >= 100.0 -> 
                    "🔴 ${category} budget EXCEEDED"
                budgetStatus.percentageUsed >= 85.0 -> 
                    "⚠️ ${category} budget ${budgetStatus.percentageUsed.toInt()}% used"
                else -> null
            }
            
            if (alertMessage != null) {
                runOnUiThread {
                    Toast.makeText(this, alertMessage, Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private fun generateDailySummary() {
        val summary = agentEngine.generateDailySummary()
        
        runOnUiThread {
            summaryText.text = summary
            // Send notification to user
            sendNotification("Daily Summary", summary)
        }
    }
    
    private fun generateWeeklySummary() {
        val summary = agentEngine.generateWeeklySummary()
        sendNotification("Weekly Report", summary)
    }
    
    private fun sendNotification(title: String, message: String) {
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        
        // Implementation would create and send notification
        // (Omitted for brevity - standard Android notification code)
    }
    
    private fun setupUIListeners() {
        val manualAddButton = findViewById<Button>(R.id.btn_add_transaction)
        val amountInput = findViewById<EditText>(R.id.input_amount)
        val merchantInput = findViewById<EditText>(R.id.input_merchant)
        
        manualAddButton.setOnClickListener {
            val amount = amountInput.text.toString()
            val merchant = merchantInput.text.toString()
            
            if (amount.isNotEmpty() && merchant.isNotEmpty()) {
                val result = agentEngine.processTransaction(
                    "₹$amount to $merchant",
                    "manual"
                )
                
                if (result != null) {
                    transactions.add(0, "${result.category} - ₹${result.amount}")
                    adapter.notifyDataSetChanged()
                    amountInput.text.clear()
                    merchantInput.text.clear()
                    Toast.makeText(this, "✅ Transaction added", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    private fun requestRequiredPermissions() {
        val permissions = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            arrayOf(
                android.Manifest.permission.POST_NOTIFICATIONS,
                android.Manifest.permission.INTERNET,
                android.Manifest.permission.READ_EXTERNAL_STORAGE
            )
        } else {
            arrayOf(
                android.Manifest.permission.INTERNET,
                android.Manifest.permission.READ_EXTERNAL_STORAGE
            )
        }
        
        for (permission in permissions) {
            if (ContextCompat.checkSelfPermission(this, permission) !=
                PackageManager.PERMISSION_GRANTED
            ) {
                ActivityCompat.requestPermissions(this, arrayOf(permission), 1)
            }
        }
    }
}


# FILE: android/app/src/main/java/com/example/expensemanager/ExpenseAgentEngine.kt

"""
ExpenseAgentEngine.kt - Bridge between Droidrun Agent and Android UI
"""

package com.example.expensemanager

import android.content.Context
import java.util.*
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit

class ExpenseAgentEngine(private val context: Context) {
    
    private val scheduler: ScheduledExecutorService = Executors.newScheduledThreadPool(2)
    private val database = ExpenseDatabase(context)
    
    fun processTransaction(text: String, sourceApp: String): TransactionResult? {
        // Extract amount and merchant using regex
        val amountPattern = """₹(\d+(?:\.\d+)?)""".toRegex()
        val merchantPattern = """to\s+([A-Za-z\s]+)""".toRegex()
        
        val amountMatch = amountPattern.find(text)
        val merchantMatch = merchantPattern.find(text)
        
        if (amountMatch != null && merchantMatch != null) {
            val amount = amountMatch.groupValues[1]
            val merchant = merchantMatch.groupValues[1].trim()
            
            // Categorize
            val category = categorizeTransaction(merchant, text)
            
            // Store in database
            database.addTransaction(
                amount = amount.toDouble(),
                merchant = merchant,
                category = category,
                sourceApp = sourceApp
            )
            
            return TransactionResult(
                amount = amount,
                merchant = merchant,
                category = category
            )
        }
        
        return null
    }
    
    private fun categorizeTransaction(merchant: String, description: String): String {
        val text = "$merchant $description".lowercase()
        
        return when {
            text.contains(Regex("coffee|starbucks|zomato|swiggy|pizza|food|lunch|dinner|restaurant")) -> "Food & Dining"
            text.contains(Regex("uber|ola|cab|taxi|metro|train|petrol|fuel|parking")) -> "Transportation"
            text.contains(Regex("electric|water|gas|internet|phone|recharge|utility")) -> "Utilities"
            text.contains(Regex("movie|netflix|spotify|ticket|entertainment")) -> "Entertainment"
            text.contains(Regex("amazon|flipkart|shopping|mall|store|cloth")) -> "Shopping"
            text.contains(Regex("hospital|doctor|medicine|gym|health")) -> "Health"
            text.contains(Regex("school|course|book|education|tuition")) -> "Education"
            else -> "Other"
        }
    }
    
    fun checkBudgetStatus(category: String): BudgetStatus {
        val budget = database.getBudget(category)
        if (budget == null) return BudgetStatus(false, 0.0)
        
        val spent = database.getCategorySpending(category)
        val percentage = (spent / budget) * 100
        
        return BudgetStatus(
            isAlertNeeded = percentage >= 80.0,
            percentageUsed = percentage
        )
    }
    
    fun generateDailySummary(): String {
        val transactions = database.getTodayTransactions()
        if (transactions.isEmpty()) return "No transactions today"
        
        val totalSpent = transactions.sumOf { it.amount }
        val byCategory = transactions.groupBy { it.category }
            .mapValues { it.value.sumOf { t -> t.amount } }
            .toList()
            .sortedByDescending { it.second }
        
        var summary = "📊 Daily Summary\n"
        summary += "💰 Total: ₹$totalSpent\n\n"
        summary += "Breakdown:\n"
        
        for ((category, amount) in byCategory) {
            val percentage = (amount / totalSpent * 100).toInt()
            summary += "• $category: ₹$amount ($percentage%)\n"
        }
        
        return summary
    }
    
    fun generateWeeklySummary(): String {
        val transactions = database.getTransactions(7)
        val totalSpent = transactions.sumOf { it.amount }
        val avgDaily = totalSpent / 7
        
        return "📈 Weekly Report\n" +
               "Total Spent: ₹$totalSpent\n" +
               "Avg Daily: ₹$avgDaily\n" +
               "Transactions: ${transactions.size}"
    }
    
    fun scheduleDailyTask(hour: Int, minute: Int, task: () -> Unit) {
        val calendar = Calendar.getInstance().apply {
            set(Calendar.HOUR_OF_DAY, hour)
            set(Calendar.MINUTE, minute)
            set(Calendar.SECOND, 0)
        }
        
        val now = Calendar.getInstance()
        val delay = if (calendar.after(now)) {
            calendar.timeInMillis - now.timeInMillis
        } else {
            calendar.add(Calendar.DATE, 1)
            calendar.timeInMillis - now.timeInMillis
        }
        
        scheduler.scheduleAtFixedRate(
            task,
            delay,
            24 * 60 * 60 * 1000,  // Every 24 hours
            TimeUnit.MILLISECONDS
        )
    }
    
    fun scheduleWeeklyTask(dayOfWeek: Int, hour: Int, minute: Int, task: () -> Unit) {
        // Similar implementation for weekly tasks
    }
    
    fun shutdown() {
        scheduler.shutdown()
    }
}


# FILE: Data Classes

"""
TransactionResult.kt - Result from transaction processing
"""

package com.example.expensemanager

data class TransactionResult(
    val amount: String,
    val merchant: String,
    val category: String
)

data class BudgetStatus(
    val isAlertNeeded: Boolean,
    val percentageUsed: Double
)

data class Transaction(
    val id: Int,
    val amount: Double,
    val merchant: String,
    val category: String,
    val timestamp: Long
)
