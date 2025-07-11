// ==================== Reset Functionality ====================
function setupResetButton() {
  const resetBtn = document.getElementById('resetDataBtn');
  const resetModal = new bootstrap.Modal(document.getElementById('resetModal'));
  const confirmReset = document.getElementById('confirmReset');

  if (!resetBtn || !confirmReset) {
    console.error("Reset elements not found");
    return;
  }

  // Show modal when reset button is clicked
  resetBtn.addEventListener('click', (e) => {
    e.preventDefault();
    resetModal.show();
  });

  // Handle actual reset when confirmed
confirmReset.addEventListener('click', () => {
    fetch("/reset", {
        method: "POST"
    }).then(() => {
        resetModal.hide();
        window.location.reload(); // Now refresh pulls empty state from the DB
    }).catch(error => {
        console.error("Reset failed:", error);
        showAlert("Reset failed. Try again.", "danger");
    });
});

}



function showAlert(message, type) {
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} position-fixed top-0 start-50 translate-middle-x mt-3`;
  alertDiv.style.zIndex = '1060';
  alertDiv.textContent = message;
  
  document.body.appendChild(alertDiv);
  
  setTimeout(() => {
    alertDiv.remove();
  }, 3000);
}




document.addEventListener('DOMContentLoaded', () => {
  // ==================== Dark Mode Toggle ====================
  const toggle = document.getElementById('darkModeToggle');
  if (!toggle) {
    console.error("Dark mode toggle not found!");
  } else {
    // Initialize theme
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Apply saved theme or fallback to system preference
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
      document.documentElement.setAttribute('data-theme', 'dark');
      toggle.checked = true;
    }

    // Toggle theme on switch change
    toggle.addEventListener('change', () => {
      if (toggle.checked) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
      }
      console.log("Theme set to:", localStorage.getItem('theme'));
      
      // Re-render charts when theme changes
      if (window.budgetCharts) {
        window.budgetCharts.renderCharts();
      }
    });

    console.log("Dark mode initialized!");
  }

  // ==================== Budget Charts ====================
  class BudgetCharts {
    constructor(transactions) {
      this.transactions = transactions;
      this.categoryChart = null;
      this.trendChart = null;
      this.init();
    }

    init() {
      this.renderCharts();
    }

    prepareCategoryData() {
      const expenses = this.transactions.filter(t => t.type === 'expense');
      const categories = [...new Set(expenses.map(t => t.category))];
      
      const categoryData = categories.map(category => 
        expenses
          .filter(t => t.category === category)
          .reduce((sum, t) => sum + Math.abs(t.amount), 0)
      );

      return {
        labels: categories,
        datasets: [{
          label: 'Expenses by Category',
          data: categoryData,
          backgroundColor: categories.map((_, i) => 
            this.getColor('expense', 0.7 - (i * 0.05))
          ),
          borderColor: categories.map(() => this.getColor('expense')),
          borderWidth: 1
        }]
      };
    }

    prepareIncomeCategoryData() {
      const incomes = this.transactions.filter(t => t.type === 'income');
      const categories = [...new Set(incomes.map(t => t.category))];
      
      const categoryData = categories.map(category => 
        incomes
          .filter(t => t.category === category)
          .reduce((sum, t) => sum + Math.abs(t.amount), 0)
      );

      return {
        labels: categories,
        datasets: [{
          label: 'Income by Category',
          data: categoryData,
          backgroundColor: categories.map((_, i) => 
            this.getColor('income', 0.7 - (i * 0.05))
          ),
          borderColor: categories.map(() => this.getColor('income')),
          borderWidth: 1
        }]
      };
    }

    prepareTrendData() {
      const now = new Date();
      const sixMonthsAgo = new Date(now);
      sixMonthsAgo.setMonth(now.getMonth() - 5);
      
      const recentTransactions = this.transactions.filter(t => {
        const tDate = new Date(t.date || now);
        return tDate >= sixMonthsAgo;
      });

      const months = Array.from({ length: 6 }, (_, i) => {
        const date = new Date();
        date.setMonth(date.getMonth() - (5 - i));
        return date.toLocaleString('default', { month: 'short' });
      });

      const monthlyData = months.map((month, i) => {
        const currentMonth = new Date().getMonth() - (5 - i);
        const year = new Date().getFullYear() - (currentMonth < 0 ? 1 : 0);
        const monthIndex = (currentMonth + 12) % 12;
        
        return {
          income: recentTransactions
            .filter(t => {
              const tDate = new Date(t.date || new Date());
              return t.type === 'income' && 
                     tDate.getMonth() === monthIndex && 
                     tDate.getFullYear() === year;
            })
            .reduce((sum, t) => sum + t.amount, 0),
          expense: recentTransactions
            .filter(t => {
              const tDate = new Date(t.date || new Date());
              return t.type === 'expense' && 
                     tDate.getMonth() === monthIndex && 
                     tDate.getFullYear() === year;
            })
            .reduce((sum, t) => sum + Math.abs(t.amount), 0)
        };
      });

      return {
        labels: months,
        datasets: [
          {
            label: 'Income',
            data: monthlyData.map(m => m.income),
            borderColor: this.getColor('income'),
            backgroundColor: this.getColor('income', 0.1),
            tension: 0.3,
            fill: true
          },
          {
            label: 'Expenses',
            data: monthlyData.map(m => m.expense),
            borderColor: this.getColor('expense'),
            backgroundColor: this.getColor('expense', 0.1),
            tension: 0.3,
            fill: true
          }
        ]
      };
    }

    prepareBalanceTrendData() {
      const sortedTransactions = [...this.transactions].sort((a, b) => new Date(a.date) - new Date(b.date));
      let balance = 0;
      const balanceData = [];
      const dates = [];

      sortedTransactions.forEach(t => {
        if (t.type === 'income') {
          balance += t.amount;
        } else {
          balance -= t.amount;
        }
        balanceData.push(balance);
        dates.push(new Date(t.date).toLocaleDateString());
      });

      return {
        labels: dates,
        datasets: [
          {
            label: 'Balance',
            data: balanceData,
            borderColor: this.getColor('balance'),
            backgroundColor: this.getColor('balance', 0.1),
            tension: 0.3,
            fill: true
          }
        ]
      };
    }

    getColor(type, opacity = 1) {
      const rootStyles = getComputedStyle(document.documentElement);
      let colorValue;

      switch (type) {
        case 'income':
          colorValue = rootStyles.getPropertyValue('--income-color').trim();
          break;
        case 'expense':
          colorValue = rootStyles.getPropertyValue('--expense-color').trim();
          break;
        case 'balance':
          colorValue = rootStyles.getPropertyValue('--balance-color').trim();
          break;
        default:
          colorValue = rootStyles.getPropertyValue('--balance-color').trim(); // Fallback
      }

      // Convert hex to rgba if necessary, or just append opacity to rgb/rgba
      if (colorValue.startsWith('#')) {
        const hex = colorValue.slice(1);
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);
        return `rgba(${r}, ${g}, ${b}, ${opacity})`;
      } else if (colorValue.startsWith('rgb(')) {
        return colorValue.replace('rgb(', 'rgba(').replace(')', `, ${opacity})`);
      } else if (colorValue.startsWith('rgba(')) {
        // Replace existing alpha with new opacity
        const parts = colorValue.split(',');
        parts[3] = ` ${opacity})`;
        return parts.join(',');
      }
      return colorValue; // Return as is if not a recognized format
    }

    getBaseOptions() {
      const isDarkMode = document.documentElement.hasAttribute('data-theme');
      const textColor = isDarkMode ? 'rgba(255, 255, 255, 0.87)' : 'rgba(0, 0, 0, 0.87)';
      const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)';

      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: textColor }
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const label = context.dataset.label || '';
                const value = context.raw || 0;
                return `${label}: R${value.toFixed(2)}`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: gridColor, display: false },
            ticks: { color: textColor }
          },
          y: {
            grid: { color: gridColor },
            ticks: { 
              color: textColor,
              callback: (value) => `R${value}`
            }
          }
        }
      };
    }

    renderCharts() {
      // Render Category Chart (Doughnut)
      const categoryCtx = document.getElementById('categoryChart')?.getContext('2d');
      if (categoryCtx) {
        if (this.categoryChart) this.categoryChart.destroy();
        this.categoryChart = new Chart(categoryCtx, {
          type: 'doughnut',
          data: this.prepareCategoryData(),
          options: this.getBaseOptions()
        });
      } else {
        console.warn("Category chart canvas not found");
      }

      // Render Income Category Chart (Doughnut)
      const incomeCategoryCtx = document.getElementById('incomeCategoryChart')?.getContext('2d');
      if (incomeCategoryCtx) {
        if (this.incomeCategoryChart) this.incomeCategoryChart.destroy();
        this.incomeCategoryChart = new Chart(incomeCategoryCtx, {
          type: 'doughnut',
          data: this.prepareIncomeCategoryData(),
          options: this.getBaseOptions()
        });
      } else {
        console.warn("Income category chart canvas not found");
      }

      // Render Trend Chart (Line)
      const trendCtx = document.getElementById('monthlyTrendChart')?.getContext('2d');
      if (trendCtx) {
        if (this.trendChart) this.trendChart.destroy();
        this.trendChart = new Chart(trendCtx, {
          type: 'line',
          data: this.prepareTrendData(),
          options: this.getBaseOptions()
        });
      } else {
        console.warn("Trend chart canvas not found");
      }

      // Render Balance Trend Chart (Line)
      const balanceTrendCtx = document.getElementById('balanceTrendChart')?.getContext('2d');
      if (balanceTrendCtx) {
        if (this.balanceTrendChart) this.balanceTrendChart.destroy();
        this.balanceTrendChart = new Chart(balanceTrendCtx, {
          type: 'line',
          data: this.prepareBalanceTrendData(),
          options: this.getBaseOptions()
        });
      } else {
        console.warn("Balance trend chart canvas not found");
      }
    }
  }

  // Initialize Budget Charts if data is available
  const transactionsDataEl = document.getElementById('transactions-data');
  if (transactionsDataEl) {
    try {
      const transactions = JSON.parse(transactionsDataEl.textContent);
      window.budgetCharts = new BudgetCharts(transactions);
    } catch (e) {
      console.error("Error parsing transactions data:", e);
    }
  }

  setupResetButton();

  // ==================== Edit and Delete Modals ====================
  const editModalElement = document.getElementById('editModal');
  const deleteModalElement = document.getElementById('deleteModal');

  if (editModalElement && deleteModalElement) {
    const editModal = new bootstrap.Modal(editModalElement);
    const deleteModal = new bootstrap.Modal(deleteModalElement);

    document.querySelectorAll('.edit-btn').forEach(button => {
      button.addEventListener('click', function() {
        const transactionId = this.dataset.id;
        const description = this.dataset.description;
        const amount = this.dataset.amount;
        const type = this.dataset.type;
        const category = this.dataset.category;

        document.getElementById('edit-description').value = description;
        document.getElementById('edit-amount').value = amount;
        document.getElementById('edit-type').value = type;
        document.getElementById('edit-category').value = category;

        const editForm = document.getElementById('editForm');
        editForm.action = `/edit/${transactionId}`;

        editModal.show();
      });
    });

    document.querySelectorAll('.delete-btn').forEach(button => {
      button.addEventListener('click', function() {
        const transactionId = this.dataset.id;
        const deleteForm = document.getElementById('deleteForm');
        deleteForm.action = `/delete/${transactionId}`;

        deleteModal.show();
      });
    });
  } else {
    console.error("Edit or Delete modal elements not found!");
  }
});