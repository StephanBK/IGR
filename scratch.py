import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Data
data = {
    'Department': ['Meade, CO', 'Pinole, CA', 'Moab', 'Utah', 'Evansville, IN',
                   'Hondo, TX', 'Maryville, MO', 'Bastrop', 'San Diego Fire'],
    'Stage': ['T&E', 'T&E', 'Paid contract', 'T&E', 'T&E', 'T&E', 'T&E', 'T&E', 'T&E'],
    'Date': ['03/2024', '06/2024', '09/2024', '10/2024', '10/2024',
             '11/2024', '11/2024', '01/2025', '01/2025']
}

# Convert to DataFrame
df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'], format='%m/%Y')

# Variation 1: Horizontal timeline with arrows
plt.figure(figsize=(12, 3))
for i, (date, dept, stage) in enumerate(zip(df['Date'], df['Department'], df['Stage'])):
    plt.plot([date, date], [0, 1], color='black', lw=1, linestyle='--', alpha=0.7)
    plt.scatter(date, 1, color='skyblue', s=100)
    plt.text(date, 1.05, dept, rotation=45, ha='right', fontsize=9)
    plt.text(date, 0.95, stage, rotation=45, ha='left', fontsize=8)

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.xticks(rotation=45)
plt.yticks([])
plt.title("Horizontal Timeline with Arrows")
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Variation 2: Vertical timeline
plt.figure(figsize=(5, 10))
for i, (date, dept, stage) in enumerate(zip(df['Date'], df['Department'], df['Stage'])):
    plt.plot([0, 1], [date, date], color='black', lw=1, linestyle='--', alpha=0.7)
    plt.scatter(0.5, date, color='skyblue', s=100)
    plt.text(0.55, date, dept, fontsize=9, va='center')
    plt.text(0.45, date, stage, fontsize=8, va='center', ha='right')

plt.gca().yaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.gca().yaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.xticks([])
plt.title("Vertical Timeline")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Variation 3: Curved timeline
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df['Date'], [0]*len(df), marker='o', markersize=8, color='skyblue', linewidth=2)
for i, (date, dept, stage) in enumerate(zip(df['Date'], df['Department'], df['Stage'])):
    ax.annotate(f'{dept}\n({stage})', xy=(date, 0), xytext=(date, 0.5 if i % 2 == 0 else -0.5),
                arrowprops=dict(facecolor='black', arrowstyle='->', lw=1),
                fontsize=9, ha='center', va='center')

ax.set_yticks([])
ax.set_title("Curved Timeline")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.xticks(rotation=45)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()