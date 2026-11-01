# ============================================
# MAPREDUCE VISUALIZATION
# IPL Season-wise Player Performance
# ============================================

library(ggplot2)
library(dplyr)
library(readr)

# --------------------------------------------
# File paths
# --------------------------------------------

input_file <- "C:/Users/Hp/Downloads/IPLBDAMP/output/mapreduce/season_player_performance.csv"

output_dir <- "C:/Users/Hp/Downloads/IPLBDAMP/output/graphs"

# Create graph directory if it does not exist
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# --------------------------------------------
# Read MapReduce CSV
# --------------------------------------------

data <- read_csv(input_file, show_col_types = FALSE)

# --------------------------------------------
# Clean column names
# --------------------------------------------

data <- data %>%
  rename(
    Season = `Season`,
    Player = `Player Name`,
    Runs = `Runs`,
    Wickets = `Wickets`
  )

# --------------------------------------------
# Convert numeric columns
# --------------------------------------------

data$Runs <- as.numeric(data$Runs)
data$Wickets <- as.numeric(data$Wickets)

# ============================================
# GRAPH 1
# Top 10 Players by Total IPL Runs
# ============================================

top_runs <- data %>%
  group_by(Player) %>%
  summarise(
    Total_Runs = sum(Runs, na.rm = TRUE)
  ) %>%
  arrange(desc(Total_Runs)) %>%
  slice_head(n = 10)

top_runs$Player <- factor(
  top_runs$Player,
  levels = top_runs$Player[order(top_runs$Total_Runs)]
)

plot1 <- ggplot(
  top_runs,
  aes(x = Player, y = Total_Runs)
) +
  geom_col() +
  coord_flip() +
  labs(
    title = "Top 10 IPL Players by Total Runs",
    subtitle = "Aggregated from Hadoop MapReduce season-wise output",
    x = "Player",
    y = "Total Runs"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 21, face = "bold"),
    plot.subtitle = element_text(size = 12, face = "bold"),
    axis.title = element_text(size = 12, face = "bold"),
    axis.text = element_text(size = 11, face = "bold")
  )

ggsave(
  filename = file.path(output_dir, "08_mapreduce_top_players.png"),
  plot = plot1,
  width = 10,
  height = 7,
  dpi = 300
)

# ============================================
# GRAPH 2
# Top 10 Players by Total Wickets
# ============================================

top_wickets <- data %>%
  group_by(Player) %>%
  summarise(
    Total_Wickets = sum(Wickets, na.rm = TRUE)
  ) %>%
  arrange(desc(Total_Wickets)) %>%
  slice_head(n = 10)

top_wickets$Player <- factor(
  top_wickets$Player,
  levels = top_wickets$Player[order(top_wickets$Total_Wickets)]
)

plot2 <- ggplot(
  top_wickets,
  aes(x = Player, y = Total_Wickets)
) +
  geom_col() +
  coord_flip() +
  labs(
    title = "Top 10 IPL Players by Total Wickets",
    subtitle = "Aggregated from Hadoop MapReduce season-wise output",
    x = "Player",
    y = "Total Wickets"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 21, face = "bold"),
    plot.subtitle = element_text(size = 12, face = "bold"),
    axis.title = element_text(size = 12, face = "bold"),
    axis.text = element_text(size = 11, face = "bold")
  )

ggsave(
  filename = file.path(output_dir, "09_mapreduce_top_wicket_takers.png"),
  plot = plot2,
  width = 10,
  height = 7,
  dpi = 300
)

# ============================================
# GRAPH 3
# Virat Kohli Season-wise Runs
# ============================================

kohli <- data %>%
  filter(
    tolower(Player) == "v kohli"
  ) %>%
  group_by(Season, Player) %>%
  summarise(
    Runs = sum(Runs, na.rm = TRUE),
    .groups = "drop"
  )

if (nrow(kohli) > 0) {

  plot3 <- ggplot(
    kohli,
    aes(x = Season, y = Runs, group = 1)
  ) +
    geom_line(linewidth = 1.2) +
    geom_point(size = 3) +
    labs(
      title = "Virat Kohli - Season-wise IPL Runs",
      subtitle = "Hadoop MapReduce output",
      x = "Season",
      y = "Runs"
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(size = 21, face = "bold"),
      plot.subtitle = element_text(size = 12, face = "bold"),
      axis.title = element_text(size = 12, face = "bold"),
      axis.text.x = element_text(
        size = 10,
        face = "bold",
        angle = 45,
        hjust = 1
      ),
      axis.text.y = element_text(size = 11, face = "bold")
    )

  ggsave(
    filename = file.path(
      output_dir,
      "10_mapreduce_kohli_season_performance.png"
    ),
    plot = plot3,
    width = 11,
    height = 7,
    dpi = 300
  )

} else {

  print("V Kohli was not found in the MapReduce CSV.")

}

# ============================================
# Completion message
# ============================================

print("============================================")
print("MapReduce visualization completed successfully.")
print("Graphs saved in:")
print(output_dir)
print("============================================")
