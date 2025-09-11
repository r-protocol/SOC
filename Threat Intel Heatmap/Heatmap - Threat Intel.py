import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Dark mode configuration
plt.style.use("dark_background")
sns.set_theme(style="darkgrid")  # Use 'dark' for minimal or 'darkgrid' for gridlines

# Set custom color and font styles
custom_params = {
    "axes.facecolor": "#0a0f2c",        # Dark navy blue to match your background
    "figure.facecolor": "#0a0f2c",
    "axes.edgecolor": "white",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "text.color": "white",
    "axes.titlecolor": "white",
    "grid.color": "#2a2f4a",
}
plt.rcParams.update(custom_params)

# Load data from CSV file
file_path = "threat_data.csv"  # Update this with the actual file path
df = pd.read_csv(file_path, encoding="ISO-8859-1")  # Use ISO-8859-1 as fallback

# Define severity order for consistent sorting
severity_order = ["Informational", "Low", "Medium", "High"]

# Create pivot table for the heatmap
heatmap_data = df.groupby(["Category", "Severity"]).size().unstack(fill_value=0)[severity_order]

# Plot heatmap with a blue color scheme suitable for dark mode
plt.figure(figsize=(10, 6))
sns.heatmap(
    heatmap_data,
    annot=True,
    cmap="Blues",           # You can try "coolwarm" or "viridis" for variety
    linewidths=0.5,
    linecolor="#1c1c3b",
    cbar_kws={"label": "Count", "orientation": "vertical"}
)

# Title and labels
plt.title("Threat Intelligence Heatmap", fontsize=14)
plt.xlabel("Severity Level", fontsize=12)
plt.ylabel("Category", fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
