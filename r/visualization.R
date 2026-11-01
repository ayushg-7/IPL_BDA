# ============================================================
# IPL BIG DATA ANALYTICS - FINAL R VISUALIZATION
# ============================================================

library(ggplot2)
library(dplyr)
library(readr)

# ============================================================
# PATHS
# ============================================================

output_dir <- "output"
graph_dir <- "output/graphs"

if (!dir.exists(graph_dir)) {
  dir.create(graph_dir, recursive = TRUE)
}


# ============================================================
# COLORS
# ============================================================

IPL_BLUE   <- "#2563EB"
IPL_ORANGE <- "#F97316"
IPL_GREEN  <- "#16A34A"
IPL_PURPLE <- "#7C3AED"
IPL_RED    <- "#DC2626"
IPL_GOLD   <- "#EAB308"
IPL_CYAN   <- "#0891B2"


# ============================================================
# COMMON THEME
# ============================================================

ipl_theme <- theme_minimal(base_size = 13) +
  theme(

    plot.title = element_text(
      size = 21,
      face = "bold",
      color = "black"
    ),

    plot.subtitle = element_text(
      size = 12,
      face = "bold",
      color = "gray30"
    ),

    axis.title = element_text(
      size = 12,
      face = "bold",
      color = "black"
    ),

    axis.text = element_text(
      size = 11,
      face = "bold",
      color = "black"
    ),

    panel.grid.major.y = element_blank(),

    panel.grid.major.x = element_line(
      color = "gray85"
    ),

    panel.grid.minor = element_blank(),

    plot.margin = margin(
      15, 25, 15, 15
    )
  )


# ============================================================
# TEAM NAME NORMALIZATION
# ============================================================

normalize_team <- function(team) {

  team <- trimws(team)

  case_when(

    team %in% c(
      "Royal Challengers Bangalore",
      "Royal Challengers Bengaluru",
      "RCB"
    ) ~ "Royal Challengers Bengaluru",

    team %in% c(
      "Kings XI Punjab",
      "Punjab Kings",
      "Punjab"
    ) ~ "Punjab Kings",

    team %in% c(
      "Delhi Daredevils",
      "Delhi Capitals",
      "Delhi"
    ) ~ "Delhi Capitals",

    team %in% c(
      "Rising Pune Supergiant",
      "Rising Pune Supergiants"
    ) ~ "Rising Pune Supergiant",

    team %in% c(
      "Pune Warriors",
      "Pune Warriors India"
    ) ~ "Pune Warriors India",

    TRUE ~ team
  )
}


# ============================================================
# LOAD DATA
# ============================================================

player_stats <- read_csv(
  file.path(
    output_dir,
    "player_statistics.csv"
  ),
  show_col_types = FALSE
)

team_stats <- read_csv(
  file.path(
    output_dir,
    "team_statistics.csv"
  ),
  show_col_types = FALSE
)

fantasy_stats <- read_csv(
  file.path(
    output_dir,
    "fantasy_recommendations.csv"
  ),
  show_col_types = FALSE
)


# ============================================================
# NORMALIZE TEAM NAMES
# ============================================================

team_stats <- team_stats %>%
  mutate(
    team = normalize_team(team)
  )


# ============================================================
# TOP 10 RUN SCORERS
# ============================================================

top_runs <- player_stats %>%
  arrange(desc(runs)) %>%
  slice_head(n = 10) %>%
  mutate(
    rank = row_number(),
    player = factor(
      player,
      levels = rev(player)
    )
  )

p1 <- ggplot(
  top_runs,
  aes(
    x = player,
    y = runs
  )
) +

  geom_col(
    fill = IPL_ORANGE,
    width = 0.65
  ) +

  geom_text(
    aes(
      label = paste0(
        "#", rank,
        "   ", runs
      )
    ),
    hjust = -0.05,
    fontface = "bold",
    size = 4
  ) +

  coord_flip() +

  scale_y_continuous(
    expand = expansion(
      mult = c(0, 0.12)
    )
  ) +

  labs(
    title = "🏏 IPL's Top Run Scorers",
    subtitle = "Highest career runs in the complete dataset",
    x = NULL,
    y = "Runs"
  ) +

  ipl_theme

print(p1)

ggsave(
  file.path(
    graph_dir,
    "01_top_run_scorers.png"
  ),
  p1,
  width = 11,
  height = 7,
  dpi = 300
)


# ============================================================
# TOP STRIKE RATE
# ============================================================

top_sr <- player_stats %>%
  filter(
    balls_faced >= 1000
  ) %>%
  arrange(desc(strike_rate)) %>%
  slice_head(n = 10) %>%
  mutate(
    player = factor(
      player,
      levels = rev(player)
    )
  )

p2 <- ggplot(
  top_sr,
  aes(
    x = player,
    y = strike_rate
  )
) +

  geom_col(
    fill = IPL_PURPLE,
    width = 0.65
  ) +

  geom_text(
    aes(
      label = round(
        strike_rate,
        1
      )
    ),
    hjust = -0.15,
    fontface = "bold",
    size = 4
  ) +

  coord_flip() +

  scale_y_continuous(
    expand = expansion(
      mult = c(0, 0.12)
    )
  ) +

  labs(
    title = "⚡ Most Explosive IPL Batters",
    subtitle = "Minimum 1000 balls faced",
    x = NULL,
    y = "Strike Rate"
  ) +

  ipl_theme

print(p2)

ggsave(
  file.path(
    graph_dir,
    "02_top_strike_rate.png"
  ),
  p2,
  width = 11,
  height = 7,
  dpi = 300
)


# ============================================================
# TOP WICKET TAKERS
# ============================================================

top_wickets <- player_stats %>%
  filter(
    balls_bowled > 0
  ) %>%
  arrange(desc(wickets)) %>%
  slice_head(n = 10) %>%
  mutate(
    player = factor(
      player,
      levels = rev(player)
    )
  )

p3 <- ggplot(
  top_wickets,
  aes(
    x = player,
    y = wickets
  )
) +

  geom_col(
    fill = IPL_RED,
    width = 0.65
  ) +

  geom_text(
    aes(
      label = wickets
    ),
    hjust = -0.15,
    fontface = "bold",
    size = 4
  ) +

  coord_flip() +

  scale_y_continuous(
    expand = expansion(
      mult = c(0, 0.12)
    )
  ) +

  labs(
    title = "🎯 IPL's Top Wicket Takers",
    subtitle = "Most wickets in the complete dataset",
    x = NULL,
    y = "Wickets"
  ) +

  ipl_theme

print(p3)

ggsave(
  file.path(
    graph_dir,
    "03_top_wicket_takers.png"
  ),
  p3,
  width = 11,
  height = 7,
  dpi = 300
)


# ============================================================
# BEST ECONOMY
# Minimum 100 overs = 600 balls
# ============================================================

top_economy <- player_stats %>%
  filter(
    balls_bowled >= 600,
    economy > 0
  ) %>%
  arrange(economy) %>%
  slice_head(n = 10) %>%
  mutate(
    player = factor(
      player,
      levels = rev(player)
    )
  )

p4 <- ggplot(
  top_economy,
  aes(
    x = player,
    y = economy
  )
) +

  geom_col(
    fill = IPL_GREEN,
    width = 0.65
  ) +

  geom_text(
    aes(
      label = sprintf(
        "%.2f",
        economy
      )
    ),
    hjust = -0.15,
    fontface = "bold",
    size = 4
  ) +

  coord_flip() +

  scale_y_continuous(
    expand = expansion(
      mult = c(0, 0.15)
    )
  ) +

  labs(
    title = "🛡️ Most Economical IPL Bowlers",
    subtitle = "Minimum 100 overs bowled",
    x = NULL,
    y = "Economy Rate"
  ) +

  ipl_theme

print(p4)

ggsave(
  file.path(
    graph_dir,
    "04_best_economy_bowlers.png"
  ),
  p4,
  width = 11,
  height = 7,
  dpi = 300
)


# ============================================================
# TEAM WIN PERCENTAGE
# ALL AVAILABLE MATCHES 2008-2026
# ============================================================

team_win <- team_stats %>%

  # Combine duplicate historical names
  group_by(team) %>%

  summarise(
    matches = sum(matches),
    wins = sum(wins),
    losses = sum(losses),
    .groups = "drop"
  ) %>%

  mutate(
    win_percentage =
      (wins / matches) * 100
  ) %>%

  arrange(
    desc(win_percentage)
  ) %>%

  mutate(
    team = factor(
      team,
      levels = rev(team)
    )
  )


p5 <- ggplot(
  team_win,
  aes(
    x = team,
    y = win_percentage
  )
) +

  geom_col(
    fill = IPL_BLUE,
    width = 0.65
  ) +

  geom_text(
    aes(
      label = paste0(
        round(
          win_percentage,
          1
        ),
        "%"
      )
    ),
    hjust = -0.1,
    fontface = "bold",
    size = 3.8
  ) +

  coord_flip() +

  scale_y_continuous(
    limits = c(
      0,
      100
    ),
    breaks = seq(
      0,
      100,
      20
    ),
    expand = expansion(
      mult = c(0, 0.02)
    )
  ) +

  labs(
    title = "🏆 IPL Team Win Percentage",
    subtitle = "All available IPL matches from 2008–2026 | Historical names combined",
    x = NULL,
    y = "Win Percentage"
  ) +

  ipl_theme

print(p5)

ggsave(
  file.path(
    graph_dir,
    "05_team_win_percentage.png"
  ),
  p5,
  width = 11,
  height = 8,
  dpi = 300
)


# ============================================================
# FANTASY RECOMMENDATIONS
# Minimum 50 matches
# ============================================================

if ("matches" %in% names(fantasy_stats)) {

  fantasy_filtered <- fantasy_stats %>%
    filter(
      matches >= 50
    )

} else if (
  "matches_played" %in%
  names(fantasy_stats)
) {

  fantasy_filtered <- fantasy_stats %>%
    filter(
      matches_played >= 50
    )

} else {

  stop(
    "Fantasy file does not contain matches or matches_played."
  )
}


# ============================================================
# FANTASY RATING /10
# ============================================================

max_score <- max(
  fantasy_filtered$fantasy_score,
  na.rm = TRUE
)

fantasy_filtered <- fantasy_filtered %>%

  mutate(
    fantasy_rating =
      (fantasy_score / max_score) * 10
  )


top_fantasy <- fantasy_filtered %>%

  arrange(
    desc(fantasy_rating)
  ) %>%

  slice_head(n = 10) %>%

  mutate(
    rank = row_number(),

    player = factor(
      player,
      levels = rev(player)
    )
  )


# ============================================================
# FANTASY GRAPH
# ============================================================

p6 <- ggplot(
  top_fantasy,
  aes(
    x = player,
    y = fantasy_rating
  )
) +

  geom_col(
    fill = IPL_GOLD,
    width = 0.65
  ) +

  geom_text(
    aes(
      label = paste0(
        round(
          fantasy_rating,
          1
        ),
        " / 10"
      )
    ),
    hjust = -0.05,
    fontface = "bold",
    size = 3.8
  ) +

  coord_flip() +

  scale_y_continuous(
    limits = c(
      0,
      10
    ),
    breaks = seq(
      0,
      10,
      2
    ),
    expand = expansion(
      mult = c(0, 0.08)
    )
  ) +

  labs(
    title = "⭐ Fantasy Player Recommendations",
    subtitle = "Minimum 50 IPL matches | Rating normalized to 10",
    x = NULL,
    y = "Fantasy Rating / 10"
  ) +

  ipl_theme

print(p6)

ggsave(
  file.path(
    graph_dir,
    "06_fantasy_recommendations.png"
  ),
  p6,
  width = 11,
  height = 7,
  dpi = 300
)


# ============================================================
# FANTASY PERFORMANCE MAP
# ============================================================

if (
  "average_fantasy_points" %in%
  names(fantasy_filtered)
  &&
  "consistency" %in%
  names(fantasy_filtered)
) {

  fantasy_profile <- fantasy_filtered %>%

    filter(
      is.finite(
        average_fantasy_points
      ),
      is.finite(
        consistency
      )
    ) %>%

    arrange(
      desc(fantasy_rating)
    ) %>%

    slice_head(n = 15)


  p7 <- ggplot(
    fantasy_profile,
    aes(
      x = consistency,
      y = average_fantasy_points,
      size = fantasy_rating
    )
  ) +

    geom_point(
      alpha = 0.8,
      color = IPL_CYAN
    ) +

    geom_text(
      aes(
        label = player
      ),
      vjust = -1.2,
      size = 3,
      fontface = "bold"
    ) +

    scale_size_continuous(
      range = c(
        3,
        9
      )
    ) +

    labs(
      title = "📈 Fantasy Performance Map",
      subtitle = "Consistency vs average fantasy points",
      x = "Consistency",
      y = "Average Fantasy Points",
      size = "Fantasy Rating"
    ) +

    ipl_theme

  print(p7)

  ggsave(
    file.path(
      graph_dir,
      "07_fantasy_performance_map.png"
    ),
    p7,
    width = 11,
    height = 7,
    dpi = 300
  )
}


# ============================================================
# FANTASY TOP 11
# ============================================================

fantasy_top11_file <- file.path(
  output_dir,
  "fantasy_top_11.csv"
)

if (
  file.exists(
    fantasy_top11_file
  )
) {

  fantasy_top11 <- read_csv(
    fantasy_top11_file,
    show_col_types = FALSE
  )

  cat("\n")
  cat("============================================\n")
  cat("              FANTASY TOP 11\n")
  cat("============================================\n")

  print(
    fantasy_top11
  )
}


# ============================================================
# COMPLETE
# ============================================================

cat("\n")
cat("============================================\n")
cat("        FINAL R VISUALIZATION COMPLETE\n")
cat("============================================\n")

cat("\nGraphs saved to:\n")
cat("output/graphs/\n")

cat("\nFilters:\n")
cat("• Economy: minimum 100 overs\n")
cat("• Fantasy: minimum 50 matches\n")
cat("• Team win percentage: all available matches\n")
cat("• Historical team names combined\n")
cat("• Fantasy rating normalized to /10\n")

cat("\nCurrent team names used:\n")
cat("• Royal Challengers Bengaluru\n")
cat("• Punjab Kings\n")
cat("• Delhi Capitals\n")
cat("• Chennai Super Kings\n")
cat("• Mumbai Indians\n")
cat("• Kolkata Knight Riders\n")
cat("• Rajasthan Royals\n")
cat("• Sunrisers Hyderabad\n")
cat("• Gujarat Titans\n")
cat("• Lucknow Super Giants\n")

cat("\n============================================\n")