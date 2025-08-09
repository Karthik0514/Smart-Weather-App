from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie, QFont, QPixmap
from weather_api import (
    get_weather_data, get_hourly_forecast, get_five_day_forecast,
    get_temperature_trend, get_uv_index, get_air_quality
)
from clothing_advice import get_clothing_advice
from song_suggestions import get_daily_song
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
import os
from sunrise_sunset import get_sunrise_sunset
from extras import get_daily_quote, get_random_fun_fact, get_today_in_history
from health_tips import get_health_tip
from auto_location import get_user_location
from weather_alerts import get_coordinates, get_weather_alerts
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QTimer


class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Weather App")
        self.setGeometry(100, 100, 1600, 900)
        self.setWindowIcon(QIcon("app_icon.png"))

        self.background_label = QLabel(self)
        self.background_label.setScaledContents(True)

        local_hour = datetime.now().hour
        default_gif = "assets/day.gif" if 6 <= local_hour < 18 else "assets/night.gif"
        self.movie = QMovie(default_gif)
        self.background_label.setMovie(self.movie)
        self.movie.start()

        self.scroll_area = QScrollArea(self.background_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent;")

        self.overlay_widget = QWidget()
        self.overlay_layout = QVBoxLayout(self.overlay_widget)
        self.overlay_layout.setContentsMargins(50, 50, 50, 50)
        self.overlay_layout.setSpacing(20)
        self.overlay_widget.setStyleSheet("background: transparent;")
        self.scroll_area.setWidget(self.overlay_widget)

        def create_section(title, widget):
            section = QFrame()
            section.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); border-radius: 15px;")
            layout = QVBoxLayout(section)
            label = QLabel(title)
            label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
            layout.addWidget(label)
            layout.addWidget(widget)
            return section

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter city name")
        self.city_input.setMaximumWidth(300)
        self.city_input.setStyleSheet("padding: 6px; font-size: 16px;")

        self.submit_button = QPushButton("Get Weather")
        self.submit_button.setMaximumWidth(150)
        self.submit_button.clicked.connect(self.fetch_weather)
        
        # === LOADING SCREEN CHANGES ===
        self.loading_overlay = QWidget(self)
        self.loading_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        self.loading_overlay.hide()

        overlay_layout = QVBoxLayout(self.loading_overlay)
        overlay_layout.setAlignment(Qt.AlignCenter)

        self.loading_gif_label = QLabel()
        self.loading_gif_label.setAlignment(Qt.AlignCenter)
        self.loading_movie = QMovie("assets/loading.gif")  
        self.loading_gif_label.setMovie(self.loading_movie)

        self.loading_text_label = QLabel("Loading Weather Data...")
        self.loading_text_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.loading_text_label.setAlignment(Qt.AlignCenter)

        overlay_layout.addWidget(self.loading_gif_label)
        overlay_layout.addWidget(self.loading_text_label)
        # === END LOADING SCREEN CHANGES ===

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.city_input)
        input_layout.addWidget(self.submit_button)
        input_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding))
        input_widget = QWidget()
        input_widget.setLayout(input_layout)

        self.weather_info = QLabel("")
        self.weather_info.setWordWrap(True)
        self.weather_info.setFont(QFont("Arial", 14))
        self.weather_info.setStyleSheet("color: white;")
        weather_section = create_section("🌍 Current Weather", self.weather_info)

        self.forecast_scroll = QScrollArea()
        self.forecast_scroll.setWidgetResizable(True)
        self.forecast_scroll.setFixedHeight(130)
        self.forecast_scroll.setStyleSheet("background: transparent;")
        self.forecast_container = QWidget()
        self.forecast_layout = QHBoxLayout(self.forecast_container)
        self.forecast_layout.setContentsMargins(0, 0, 0, 0)
        self.forecast_layout.setSpacing(20)
        self.forecast_scroll.setWidget(self.forecast_container)
        forecast_section = create_section("🕓 Hourly Forecast", self.forecast_scroll)

        self.graph_label = QLabel()
        self.graph_label.setFixedHeight(300)
        self.graph_label.setStyleSheet("color: white; font-size: 14px;")
        self.graph_label.setAlignment(Qt.AlignCenter)
        graph_section = create_section("📈 Temperature Trend", self.graph_label)

        self.five_day_label = QLabel("📅 5-day forecast will be displayed here.")
        self.five_day_label.setStyleSheet("color: white; font-size: 16px;")
        self.five_day_label.setWordWrap(True)
        five_day_section = create_section("📅 5-Day Forecast", self.five_day_label)
        
        self.overlay_layout.addWidget(weather_section)
        
        # === Precipitation chance ===
        self.precip_label = QLabel("🌧 Chance of Precipitation: Loading...")
        self.precip_label.setWordWrap(True)
        self.precip_label.setFont(QFont("Arial", 12))
        self.precip_label.setStyleSheet("color: white;")

        precip_section = create_section("🌧 Precipitation Forecast", self.precip_label)

        # === Sunrise and Sunset ====
        self.sunrise_sunset_label = QLabel("🌅 Sunrise and sunset info goes here.")
        self.sunrise_sunset_label.setStyleSheet("color: white; font-size: 16px;")
        sun_section = create_section("🌄 Sunrise & Sunset", self.sunrise_sunset_label)

        suggestion_widget = QWidget()
        suggestion_layout = QVBoxLayout(suggestion_widget)

        self.advice_title = QLabel("🧥 Clothing Advice:")
        self.advice_title.setFont(QFont("Arial", 13, QFont.Bold))
        self.advice_title.setStyleSheet("color: white;")
        self.advice_label = QLabel("")
        self.advice_label.setWordWrap(True)
        self.advice_label.setFont(QFont("Arial", 12))
        self.advice_label.setStyleSheet("color: white;")

        self.song_title = QLabel("🎵 Song Suggestion:")
        self.song_title.setFont(QFont("Arial", 13, QFont.Bold))
        self.song_title.setStyleSheet("color: white;")
        self.song_label = QLabel("")
        self.song_label.setWordWrap(True)
        self.song_label.setFont(QFont("Arial", 12))
        self.song_label.setStyleSheet("color: white;")

        self.mood_title = QLabel("🧠 Mood Forecast:")
        self.mood_title.setFont(QFont("Arial", 13, QFont.Bold))
        self.mood_title.setStyleSheet("color: white;")
        self.mood_label = QLabel("")
        self.mood_label.setWordWrap(True)
        self.mood_label.setFont(QFont("Arial", 12))
        self.mood_label.setStyleSheet("color: white;")
        
        suggestion_layout.addWidget(self.advice_title)
        suggestion_layout.addWidget(self.advice_label)
        suggestion_layout.addWidget(self.song_title)
        suggestion_layout.addWidget(self.song_label)
        suggestion_layout.addWidget(self.mood_title)
        suggestion_layout.addWidget(self.mood_label)
        suggestions_section = create_section("💡 Suggestions", suggestion_widget)
        
        # === Extras Section ===
        extras_widget = QWidget()
        extras_layout = QVBoxLayout(extras_widget)

        self.history_title = QLabel("📜 Today in History:")
        self.history_title.setFont(QFont("Arial", 13, QFont.Bold))
        self.history_title.setStyleSheet("color: white;")
        self.history_label = QLabel("")
        self.history_label.setWordWrap(True)
        self.history_label.setFont(QFont("Arial", 12))
        self.history_label.setStyleSheet("color: white;")

        self.fact_title = QLabel("🤔 Fun Fact:")
        self.fact_title.setFont(QFont("Arial", 13, QFont.Bold))
        self.fact_title.setStyleSheet("color: white;")
        self.fact_label = QLabel("")
        self.fact_label.setWordWrap(True)
        self.fact_label.setFont(QFont("Arial", 12))
        self.fact_label.setStyleSheet("color: white;")

        self.quote_title = QLabel("📝 Daily Quote:")
        self.quote_title.setFont(QFont("Arial", 13, QFont.Bold)) 
        self.quote_title.setStyleSheet("color: white;") 
        self.quote_label = QLabel("")
        self.quote_label.setWordWrap(True)
        self.quote_label.setFont(QFont("Arial", 12))
        self.quote_label.setStyleSheet("color: white;")

        extras_layout.addWidget(self.history_title)
        extras_layout.addWidget(self.history_label)
        extras_layout.addWidget(self.fact_title)
        extras_layout.addWidget(self.fact_label)
        extras_layout.addWidget(self.quote_title)
        extras_layout.addWidget(self.quote_label)

        extras_section = create_section("✨ Extras", extras_widget)
        
        # === Health & Wellness Section ===
        health_widget = QWidget()
        health_layout = QVBoxLayout(health_widget)

        self.health_title = QLabel("🧘 Health & Wellness Tip:")
        self.health_title.setFont(QFont("Arial", 13, QFont.Bold))
        self.health_title.setStyleSheet("color: white;")
        self.health_label = QLabel("")
        self.health_label.setWordWrap(True)
        self.health_label.setFont(QFont("Arial", 12))
        self.health_label.setStyleSheet("color: white;")

        health_layout.addWidget(self.health_title)
        health_layout.addWidget(self.health_label)

        health_section = create_section("🩺 Health & Wellness", health_widget)

        self.overlay_layout.addWidget(input_widget)
        self.overlay_layout.addWidget(weather_section)
        self.overlay_layout.addWidget(precip_section)
        self.overlay_layout.addWidget(forecast_section)
        self.overlay_layout.addWidget(graph_section)
        self.overlay_layout.addWidget(five_day_section)
        self.overlay_layout.addWidget(sun_section)
        self.overlay_layout.addWidget(health_section)
        self.overlay_layout.addWidget(suggestions_section)
        self.overlay_layout.addWidget(extras_section)
       
        self.background_label_layout = QVBoxLayout(self.background_label)
        self.background_label_layout.setContentsMargins(0, 0, 0, 0)
        self.background_label_layout.addWidget(self.scroll_area)
        self.setCentralWidget(self.background_label)

        # Resize loading overlay
        self.loading_overlay.setGeometry(0, 0, self.width(), self.height())

        # Auto-detect location
        auto_city = get_user_location()
        if auto_city:
            self.city_input.setText(auto_city)
            self.fetch_weather()

        self.show()
    
    def resizeEvent(self, event):
        if hasattr(self, "background_label"):
            self.background_label.setGeometry(0, 0, self.width(), self.height())
        if hasattr(self, "scroll_area"):
            self.scroll_area.setGeometry(0, 0, self.width(), self.height())
        if hasattr(self, "loading_overlay"):  # keep overlay full size
            self.loading_overlay.setGeometry(0, 0, self.width(), self.height())

    def fetch_weather(self):
        city = self.city_input.text().strip()
        if not city:
            QMessageBox.warning(self, "Input Error", "Please enter a city name.")
            return

        # === LOADING SCREEN CHANGES ===
        self.loading_overlay.show()
        self.loading_movie.start()
        # === END LOADING SCREEN CHANGES ===

        QTimer.singleShot(100, lambda: self._perform_fetch(city))
    
    def _perform_fetch(self, city):
        try:
            data = get_weather_data(city)
            if not data:
                self.weather_info.setText("❗ Error: Could not retrieve data.")
                self.loading_overlay.hide()
                return

            temp = data["temp"]
            condition = data["condition"]
            humidity = data["humidity"]
            wind = data["wind_speed"]
            self.health_label.setText(get_health_tip(condition, temp))
            uv_index = get_uv_index(city)
            air_quality = get_air_quality(city)

            self.weather_info.setText(
                f"🌍 Weather in {city}:\n"
                f"🌡 Temperature: {temp}°C\n"
                f"🌤 Condition: {condition.title()}\n"
                f"💧 Humidity: {humidity}%\n"
                f"🍃 Wind Speed: {wind} m/s\n"
                f"🔆 UV Index: {uv_index}\n"
                f"🌫 Air Quality: {air_quality}"
            )
 
            self.advice_label.setText(get_clothing_advice(temp, condition))
            self.song_label.setText(get_daily_song(condition))
            self.mood_label.setText(self.get_mood_forecast(condition))
            self.sunrise_sunset_label.setText(get_sunrise_sunset(city))
            self.history_label.setText(get_today_in_history())
            self.update_background(condition.lower())
            hourly_data = get_hourly_forecast(city)
            self.update_hourly_forecast(hourly_data)

            avg_pop = sum(int(entry["pop"]) for entry in hourly_data if "pop" in entry) / len(hourly_data) 
            self.precip_label.setText(f"🌧 Average Chance of Precipitation (Next 8 hrs): {avg_pop:.1f}%")

            self.update_five_day_forecast(get_five_day_forecast(city))
            self.update_graph(get_temperature_trend(city))
            self.fact_label.setText(get_random_fun_fact())
            self.quote_label.setText(get_daily_quote())

            from config import OPENWEATHER_API_KEY
            lat, lon = get_coordinates(city, OPENWEATHER_API_KEY)
            if lat and lon:
                alerts = get_weather_alerts(lat, lon, OPENWEATHER_API_KEY)
                if alerts:
                    for alert in alerts:
                        event = alert.get("event", "⚠️ Weather Alert")
                        description = alert.get("description", "No description available.")
                        QMessageBox.warning(self, f"⚠️ {event}", description)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

        # === LOADING SCREEN CHANGES ===
        self.loading_overlay.hide()
        self.loading_movie.stop()
        # === END LOADING SCREEN CHANGES ===

    def update_background(self, condition):
        gif_path = "assets/default.gif"
        if "rain" in condition:
            gif_path = "assets/rain.gif"
        elif "clear" in condition or "sun" in condition:
            gif_path = "assets/clear.gif"
        elif "cloud" in condition:
            gif_path = "assets/clouds.gif"
        elif "snow" in condition:
            gif_path = "assets/snow.gif"
        elif "storm" in condition:
            gif_path = "assets/storm.gif"
        elif "drizzle" in condition:
            gif_path = "assets/drizzle.gif"

        self.movie.stop()
        self.movie = QMovie(gif_path)
        self.background_label.setMovie(self.movie)
        self.movie.start()

    def update_hourly_forecast(self, forecast_data):
        for i in reversed(range(self.forecast_layout.count())):
            widget = self.forecast_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not forecast_data:
            return

        for entry in forecast_data:
            time = entry["time"]
            temp = entry["temp"]
            icon = entry["icon"]
            block = QLabel(f"{time[:5]}\n{temp}°C\n{self.map_icon(icon)}")
            block.setAlignment(Qt.AlignCenter)
            block.setStyleSheet(
                "color: white; padding: 10px; border: 1px solid white; border-radius: 10px; font-size: 16px;"
            )

            self.forecast_layout.addWidget(block)

    def update_five_day_forecast(self, forecast):
        if not forecast:
            self.five_day_label.setText("No forecast data available.")
            return

        text = ""
        for day in forecast:
            condition = day['condition'].lower()
            emoji = self.map_icon(condition)
            text += f"{emoji} {day['date']}: {day['min_temp']}°C - {day['max_temp']}°C, {day['condition']}\n"
        self.five_day_label.setText(text)

    def update_graph(self, trend_data):
        if not trend_data:
            self.graph_label.setText("No trend data.")
            return

        from matplotlib import pyplot as plt
        from matplotlib import rcParams

        dates = [d['date'] for d in trend_data]
        temps = [d['avg_temp'] for d in trend_data]

        fig, ax = plt.subplots(figsize=(8, 3), dpi=120)
        ax.plot(dates, temps, marker='o', color='cyan')
        ax.set_title("Temperature Trend")
        ax.set_xlabel("Date")
        ax.set_ylabel("Avg Temp (°C)")
        ax.grid(True)
        fig.tight_layout()

        graph_path = "temp_trend.png"
        fig.savefig(graph_path, bbox_inches='tight')
        plt.close(fig)

        pixmap = QPixmap(graph_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.graph_label.width(),
                self.graph_label.height(),
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )
            self.graph_label.setPixmap(scaled_pixmap)

    def map_icon(self, icon_name):
        mapping = {
            "clear-day": "☀️", "clear-night": "🌙", "partly-cloudy-day": "⛅",
            "partly-cloudy-night": "🌥", "cloudy": "☁️", "rain": "🌧",
            "snow": "❄️", "sleet": "🌨", "wind": "💨", "fog": "🌫"
        }
        return mapping.get(icon_name, "❓")

    def get_mood_forecast(self, condition):
        condition = condition.lower()
        if "rain" in condition:
            return "A cozy, introspective vibe. Good day for books and tea."
        elif "clear" in condition or "sun" in condition:
            return "Energetic and positive vibes. Perfect for outdoor activities!"
        elif "snow" in condition:
            return "Calm and magical. Time to enjoy the winter wonderland."
        elif "storm" in condition:
            return "Intense and dramatic. Stay safe indoors."
        else:
            return "Neutral and steady. A balanced kind of day."


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_()) 