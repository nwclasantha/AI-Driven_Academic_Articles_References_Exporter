"""
Enterprise-Level GUI - Professional Modern Interface
Ultra-modern, professional design with advanced features
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from PySide6 import QtWidgets, QtCore, QtGui
from .config import ConfigManager
from .database import DatabaseManager
from .worker import WorkerManager
from .logger import LoggerManager


class StatsCard(QtWidgets.QFrame):
    """Modern statistics card widget"""

    def __init__(self, title: str, value: str = "0", icon: str = "📊"):
        super().__init__()
        self.setObjectName("statsCard")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Icon and title
        header = QtWidgets.QHBoxLayout()
        icon_lbl = QtWidgets.QLabel(icon)
        icon_lbl.setObjectName("statsIcon")
        icon_lbl.setStyleSheet("font-size: 24px;")

        title_lbl = QtWidgets.QLabel(title)
        title_lbl.setObjectName("statsTitle")

        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addStretch()

        # Value
        self.value_lbl = QtWidgets.QLabel(value)
        self.value_lbl.setObjectName("statsValue")
        self.value_lbl.setAlignment(QtCore.Qt.AlignCenter)

        layout.addLayout(header)
        layout.addWidget(self.value_lbl)

    def update_value(self, value: str):
        """Update card value"""
        self.value_lbl.setText(value)


class ModernButton(QtWidgets.QPushButton):
    """Custom modern button with icon support"""

    def __init__(self, text: str, icon: str = "", button_type: str = "default"):
        super().__init__(text)
        self.button_type = button_type
        self.setObjectName(f"modernButton_{button_type}")
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setMinimumHeight(45)

        if icon:
            # For emoji icons
            self.setText(f"{icon}  {text}")


class MainWindow(QtWidgets.QMainWindow):
    """
    Professional Modern Main Window
    """

    def __init__(self, config_manager: ConfigManager, logger_manager: LoggerManager):
        super().__init__()
        self.config_manager = config_manager
        self.logger_manager = logger_manager
        self.logger = logging.getLogger(__name__)

        self.config = config_manager.config
        self.db = DatabaseManager(self.config.db_path)
        self.worker_manager = WorkerManager()

        # Animation objects
        self.animations = []

        self._setup_ui()
        self._setup_connections()
        self._load_state()
        self._apply_animations()

    def _setup_ui(self):
        """Setup professional user interface"""
        self.setWindowTitle("IEEE Reference Extractor - Enterprise Edition v3.0")
        self.resize(self.config.window_width, self.config.window_height)
        self.setMinimumSize(1200, 800)

        # Central widget with modern layout
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top navigation bar
        nav_bar = self._create_navigation_bar()
        main_layout.addWidget(nav_bar)

        # Content area with sidebar
        content_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # Left sidebar
        sidebar = self._create_sidebar()
        content_splitter.addWidget(sidebar)

        # Main content area
        content = self._create_content_area()
        content_splitter.addWidget(content)

        # Set splitter proportions
        content_splitter.setStretchFactor(0, 1)
        content_splitter.setStretchFactor(1, 3)
        content_splitter.setSizes([300, 900])

        main_layout.addWidget(content_splitter, 1)

        # Bottom status bar
        self._create_modern_status_bar()

        # Apply professional styles
        self._apply_professional_styles()

    def _create_navigation_bar(self) -> QtWidgets.QWidget:
        """Create modern navigation bar"""
        nav = QtWidgets.QFrame()
        nav.setObjectName("navigationBar")
        nav.setFixedHeight(70)

        layout = QtWidgets.QHBoxLayout(nav)
        layout.setContentsMargins(25, 10, 25, 10)

        # Logo and title
        logo_title = QtWidgets.QHBoxLayout()

        logo = QtWidgets.QLabel("📚")
        logo.setStyleSheet("font-size: 32px;")

        title_layout = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("IEEE Reference Extractor")
        title.setObjectName("navTitle")

        subtitle = QtWidgets.QLabel("Enterprise Edition v3.0")
        subtitle.setObjectName("navSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        title_layout.setSpacing(0)

        logo_title.addWidget(logo)
        logo_title.addLayout(title_layout)
        logo_title.addSpacing(20)

        # Action buttons
        self.theme_btn = QtWidgets.QPushButton("🌙")
        self.theme_btn.setObjectName("iconButton")
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.theme_btn.setToolTip("Toggle Theme")

        self.settings_btn = QtWidgets.QPushButton("⚙️")
        self.settings_btn.setObjectName("iconButton")
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.settings_btn.setToolTip("Settings")

        self.help_btn = QtWidgets.QPushButton("❓")
        self.help_btn.setObjectName("iconButton")
        self.help_btn.setFixedSize(40, 40)
        self.help_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.help_btn.setToolTip("Help & About")

        layout.addLayout(logo_title)
        layout.addStretch()
        layout.addWidget(self.theme_btn)
        layout.addWidget(self.settings_btn)
        layout.addWidget(self.help_btn)

        return nav

    def _create_sidebar(self) -> QtWidgets.QWidget:
        """Create modern sidebar with controls"""
        sidebar = QtWidgets.QFrame()
        sidebar.setObjectName("sidebar")

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        content = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Quick Actions Section
        quick_actions = self._create_quick_actions()
        layout.addWidget(quick_actions)

        # Configuration Section
        config_section = self._create_configuration_section()
        layout.addWidget(config_section)

        # Statistics Cards
        stats = self._create_stats_cards()
        layout.addWidget(stats)

        layout.addStretch()

        scroll.setWidget(content)

        sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.addWidget(scroll)

        return sidebar

    def _create_quick_actions(self) -> QtWidgets.QGroupBox:
        """Create quick actions section"""
        group = QtWidgets.QGroupBox("📂 Quick Actions")
        group.setObjectName("modernGroup")

        layout = QtWidgets.QVBoxLayout(group)
        layout.setSpacing(12)

        # Input folder button
        self.input_btn = ModernButton("Select Input Folder", "📁", "primary")
        self.input_lbl = QtWidgets.QLabel("No folder selected")
        self.input_lbl.setObjectName("pathLabel")
        self.input_lbl.setWordWrap(True)

        # Output folder button
        self.output_btn = ModernButton("Select Output Folder", "💾", "primary")
        self.output_lbl = QtWidgets.QLabel("No folder selected")
        self.output_lbl.setObjectName("pathLabel")
        self.output_lbl.setWordWrap(True)

        # PDF count indicator
        self.pdf_count_lbl = QtWidgets.QLabel("PDFs Found: 0")
        self.pdf_count_lbl.setObjectName("infoLabel")

        layout.addWidget(self.input_btn)
        layout.addWidget(self.input_lbl)
        layout.addSpacing(10)
        layout.addWidget(self.output_btn)
        layout.addWidget(self.output_lbl)
        layout.addSpacing(10)
        layout.addWidget(self.pdf_count_lbl)

        return group

    def _create_configuration_section(self) -> QtWidgets.QGroupBox:
        """Create configuration section"""
        group = QtWidgets.QGroupBox("⚙️ Configuration")
        group.setObjectName("modernGroup")

        layout = QtWidgets.QVBoxLayout(group)
        layout.setSpacing(15)

        # Export format
        format_layout = QtWidgets.QVBoxLayout()
        format_lbl = QtWidgets.QLabel("Export Format")
        format_lbl.setObjectName("sectionLabel")

        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.setObjectName("modernCombo")
        self.format_combo.addItems(["📄 BibTeX", "📋 RIS", "💼 JSON", "📊 CSV"])
        self.format_combo.setMinimumHeight(40)

        format_layout.addWidget(format_lbl)
        format_layout.addWidget(self.format_combo)

        # Citation style
        style_layout = QtWidgets.QVBoxLayout()
        style_lbl = QtWidgets.QLabel("Citation Style")
        style_lbl.setObjectName("sectionLabel")

        self.style_combo = QtWidgets.QComboBox()
        self.style_combo.setObjectName("modernCombo")
        self.style_combo.addItems(["IEEE", "APA", "MLA", "Chicago", "Harvard"])
        self.style_combo.setMinimumHeight(40)

        style_layout.addWidget(style_lbl)
        style_layout.addWidget(self.style_combo)

        # Advanced options
        options_layout = QtWidgets.QVBoxLayout()
        options_lbl = QtWidgets.QLabel("Advanced Options")
        options_lbl.setObjectName("sectionLabel")

        self.enrich_checkbox = QtWidgets.QCheckBox("🌐 API Metadata Enrichment")
        self.enrich_checkbox.setObjectName("modernCheckbox")
        self.enrich_checkbox.setChecked(self.config.enable_crossref)
        self.enrich_checkbox.setToolTip("Enhance references using CrossRef and DOI APIs for complete metadata")

        self.ml_checkbox = QtWidgets.QCheckBox("🤖 ML-Enhanced Parsing")
        self.ml_checkbox.setObjectName("modernCheckbox")
        self.ml_checkbox.setChecked(self.config.enable_ml_parsing)
        self.ml_checkbox.setToolTip("Use machine learning algorithms for improved parsing accuracy")

        self.auto_open_checkbox = QtWidgets.QCheckBox("📂 Auto-open Output Folder")
        self.auto_open_checkbox.setObjectName("modernCheckbox")
        self.auto_open_checkbox.setChecked(True)
        self.auto_open_checkbox.setToolTip("Automatically open output folder after extraction completes")

        options_layout.addWidget(options_lbl)
        options_layout.addWidget(self.enrich_checkbox)
        options_layout.addWidget(self.ml_checkbox)
        options_layout.addWidget(self.auto_open_checkbox)

        # Control buttons
        buttons_layout = QtWidgets.QVBoxLayout()
        buttons_layout.setSpacing(10)

        self.start_btn = ModernButton("Start Extraction", "🚀", "success")
        self.start_btn.setEnabled(False)
        self.start_btn.setMinimumHeight(55)

        self.cancel_btn = ModernButton("Cancel", "⏹️", "danger")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setMinimumHeight(45)

        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.cancel_btn)

        layout.addLayout(format_layout)
        layout.addLayout(style_layout)
        layout.addLayout(options_layout)
        layout.addSpacing(10)
        layout.addLayout(buttons_layout)

        return group

    def _create_stats_cards(self) -> QtWidgets.QGroupBox:
        """Create statistics cards"""
        group = QtWidgets.QGroupBox("📈 Statistics")
        group.setObjectName("modernGroup")

        layout = QtWidgets.QVBoxLayout(group)
        layout.setSpacing(10)

        self.pdfs_card = StatsCard("PDFs", "0", "📄")
        self.refs_card = StatsCard("References", "0", "📚")
        self.time_card = StatsCard("Time", "0s", "⏱️")
        self.speed_card = StatsCard("Speed", "-", "⚡")

        layout.addWidget(self.pdfs_card)
        layout.addWidget(self.refs_card)
        layout.addWidget(self.time_card)
        layout.addWidget(self.speed_card)

        return group

    def _create_content_area(self) -> QtWidgets.QWidget:
        """Create main content area"""
        content = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Progress section
        progress_section = self._create_progress_section()
        layout.addWidget(progress_section)

        # Tabbed interface
        tabs = self._create_modern_tabs()
        layout.addWidget(tabs, 1)

        return content

    def _create_progress_section(self) -> QtWidgets.QFrame:
        """Create modern progress section"""
        frame = QtWidgets.QFrame()
        frame.setObjectName("progressFrame")

        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Status label with icon
        status_layout = QtWidgets.QHBoxLayout()
        self.status_icon = QtWidgets.QLabel("⏳")
        self.status_icon.setStyleSheet("font-size: 20px;")

        self.status_lbl = QtWidgets.QLabel("Ready to process")
        self.status_lbl.setObjectName("statusLabel")

        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_lbl)
        status_layout.addStretch()

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setObjectName("modernProgress")
        self.progress_bar.setMinimumHeight(35)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m PDFs (%p%)")

        # Current file label
        self.current_file_lbl = QtWidgets.QLabel("")
        self.current_file_lbl.setObjectName("currentFileLabel")
        self.current_file_lbl.setAlignment(QtCore.Qt.AlignCenter)

        layout.addLayout(status_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.current_file_lbl)

        return frame

    def _create_modern_tabs(self) -> QtWidgets.QTabWidget:
        """Create modern tabbed interface"""
        tabs = QtWidgets.QTabWidget()
        tabs.setObjectName("modernTabs")
        tabs.setDocumentMode(True)

        # Processing Log
        log_widget = QtWidgets.QWidget()
        log_layout = QtWidgets.QVBoxLayout(log_widget)
        log_layout.setContentsMargins(10, 10, 10, 10)

        log_toolbar = QtWidgets.QHBoxLayout()
        clear_log_btn = QtWidgets.QPushButton("🗑️ Clear")
        clear_log_btn.setObjectName("toolbarButton")
        export_log_btn = QtWidgets.QPushButton("💾 Export")
        export_log_btn.setObjectName("toolbarButton")

        log_toolbar.addWidget(QtWidgets.QLabel("Processing Log"))
        log_toolbar.addStretch()
        log_toolbar.addWidget(clear_log_btn)
        log_toolbar.addWidget(export_log_btn)

        self.log_text = QtWidgets.QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setObjectName("logText")
        self.log_text.setFont(QtGui.QFont("Consolas", 9))

        log_layout.addLayout(log_toolbar)
        log_layout.addWidget(self.log_text)

        clear_log_btn.clicked.connect(self.log_text.clear)

        tabs.addTab(log_widget, "📋 Processing Log")

        # Output Preview
        preview_widget = QtWidgets.QWidget()
        preview_layout = QtWidgets.QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(10, 10, 10, 10)

        preview_toolbar = QtWidgets.QHBoxLayout()
        copy_preview_btn = QtWidgets.QPushButton("📋 Copy")
        copy_preview_btn.setObjectName("toolbarButton")

        preview_toolbar.addWidget(QtWidgets.QLabel("Output Preview"))
        preview_toolbar.addStretch()
        preview_toolbar.addWidget(copy_preview_btn)

        self.preview_text = QtWidgets.QPlainTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setObjectName("previewText")
        self.preview_text.setFont(QtGui.QFont("Courier New", 9))

        preview_layout.addLayout(preview_toolbar)
        preview_layout.addWidget(self.preview_text)

        tabs.addTab(preview_widget, "👁️ Output Preview")

        # Database View
        db_widget = self._create_database_tab()
        tabs.addTab(db_widget, "💾 Database")

        # Statistics
        stats_widget = self._create_statistics_tab()
        tabs.addTab(stats_widget, "📊 Statistics")

        return tabs

    def _create_database_tab(self) -> QtWidgets.QWidget:
        """Create database view tab"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Toolbar
        toolbar = QtWidgets.QHBoxLayout()

        refresh_btn = QtWidgets.QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("toolbarButton")
        refresh_btn.clicked.connect(self._refresh_database_view)

        export_db_btn = QtWidgets.QPushButton("💾 Export")
        export_db_btn.setObjectName("toolbarButton")
        export_db_btn.clicked.connect(self._export_database)

        import_db_btn = QtWidgets.QPushButton("📂 Import")
        import_db_btn.setObjectName("toolbarButton")
        import_db_btn.clicked.connect(self._import_database)

        search_input = QtWidgets.QLineEdit()
        search_input.setPlaceholderText("🔍 Search references...")
        search_input.setObjectName("searchInput")
        search_input.setMinimumWidth(300)

        toolbar.addWidget(QtWidgets.QLabel("Database"))
        toolbar.addStretch()
        toolbar.addWidget(search_input)
        toolbar.addWidget(refresh_btn)
        toolbar.addWidget(export_db_btn)
        toolbar.addWidget(import_db_btn)

        # Table
        self.db_table = QtWidgets.QTableWidget()
        self.db_table.setObjectName("modernTable")
        self.db_table.setColumnCount(7)
        self.db_table.setHorizontalHeaderLabels([
            "Title", "Authors", "Year", "Journal", "DOI", "Confidence", "Actions"
        ])
        self.db_table.horizontalHeader().setStretchLastSection(False)
        self.db_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.db_table.setAlternatingRowColors(True)
        self.db_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.db_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # Record count
        self.record_count_lbl = QtWidgets.QLabel("Total Records: 0")
        self.record_count_lbl.setObjectName("infoLabel")

        layout.addLayout(toolbar)
        layout.addWidget(self.db_table)
        layout.addWidget(self.record_count_lbl)

        return widget

    def _create_statistics_tab(self) -> QtWidgets.QWidget:
        """Create statistics tab"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Toolbar
        toolbar = QtWidgets.QHBoxLayout()

        refresh_stats_btn = QtWidgets.QPushButton("🔄 Refresh")
        refresh_stats_btn.setObjectName("toolbarButton")
        refresh_stats_btn.clicked.connect(self._show_statistics)

        toolbar.addWidget(QtWidgets.QLabel("Statistics"))
        toolbar.addStretch()
        toolbar.addWidget(refresh_stats_btn)

        # Stats display
        self.stats_text = QtWidgets.QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setObjectName("statsDisplay")

        layout.addLayout(toolbar)
        layout.addWidget(self.stats_text)

        # Load initial stats
        self._show_statistics()

        return widget

    def _create_modern_status_bar(self):
        """Create modern status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.setObjectName("modernStatusBar")

        # Left side - status message
        self.status_msg = QtWidgets.QLabel("Ready")
        self.status_msg.setObjectName("statusMessage")
        self.status_bar.addWidget(self.status_msg)

        # Right side - indicators
        self.db_indicator = QtWidgets.QLabel("💾 DB: Connected")
        self.db_indicator.setObjectName("statusIndicator")

        self.api_indicator = QtWidgets.QLabel("🌐 API: Ready")
        self.api_indicator.setObjectName("statusIndicator")

        self.time_indicator = QtWidgets.QLabel(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
        self.time_indicator.setObjectName("statusIndicator")

        self.status_bar.addPermanentWidget(self.db_indicator)
        self.status_bar.addPermanentWidget(self.api_indicator)
        self.status_bar.addPermanentWidget(self.time_indicator)

        # Update time every second
        self.time_timer = QtCore.QTimer()
        self.time_timer.timeout.connect(self._update_time)
        self.time_timer.start(1000)

    def _update_time(self):
        """Update time indicator"""
        self.time_indicator.setText(f"🕒 {datetime.now().strftime('%H:%M:%S')}")

    def _apply_professional_styles(self):
        """Apply professional modern stylesheet"""
        self.setStyleSheet("""
            /* Main Window */
            QMainWindow {
                background-color: #F5F7FA;
            }

            /* Navigation Bar */
            #navigationBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-bottom: 3px solid rgba(255,255,255,0.1);
            }

            #navTitle {
                color: white;
                font-size: 22px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }

            #navSubtitle {
                color: rgba(255,255,255,0.85);
                font-size: 11px;
                letter-spacing: 1px;
            }

            #iconButton {
                background-color: rgba(255,255,255,0.15);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
            }

            #iconButton:hover {
                background-color: rgba(255,255,255,0.25);
            }

            #iconButton:pressed {
                background-color: rgba(255,255,255,0.35);
            }

            /* Sidebar */
            #sidebar {
                background-color: #FFFFFF;
                border-right: 1px solid #E5E9F2;
            }

            /* Modern Groups */
            #modernGroup {
                background-color: #FFFFFF;
                border: 1px solid #E5E9F2;
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
                font-weight: 600;
                font-size: 13px;
                color: #2D3748;
            }

            #modernGroup::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background-color: #FFFFFF;
                border-radius: 6px;
            }

            /* Modern Buttons */
            #modernButton_default {
                background-color: #6C757D;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
            }

            #modernButton_default:hover {
                background-color: #5A6268;
            }

            #modernButton_primary {
                background-color: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
            }

            #modernButton_primary:hover {
                background-color: #5568d3;
            }

            #modernButton_success {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #56ab2f, stop:1 #a8e063);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }

            #modernButton_success:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a9428, stop:1 #91c956);
            }

            #modernButton_success:disabled {
                background-color: #CCCCCC;
            }

            #modernButton_danger {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
            }

            #modernButton_danger:hover {
                background-color: #C0392B;
            }

            /* Stats Cards */
            #statsCard {
                background-color: #FFFFFF;
                border: 1px solid #E5E9F2;
                border-radius: 10px;
                padding: 10px;
            }

            #statsTitle {
                color: #718096;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            #statsValue {
                color: #2D3748;
                font-size: 24px;
                font-weight: bold;
                margin-top: 5px;
            }

            /* Labels */
            #pathLabel {
                color: #718096;
                font-size: 11px;
                font-style: italic;
                padding: 5px;
                background-color: #F7FAFC;
                border-radius: 5px;
            }

            #sectionLabel {
                color: #4A5568;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 5px;
            }

            #infoLabel {
                color: #4A5568;
                font-size: 12px;
                font-weight: 500;
                padding: 8px;
                background-color: #EDF2F7;
                border-radius: 6px;
            }

            /* Combo Boxes */
            #modernCombo {
                background-color: #FFFFFF;
                border: 2px solid #E5E9F2;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                color: #2D3748;
            }

            #modernCombo:hover {
                border: 2px solid #667eea;
            }

            #modernCombo::drop-down {
                border: none;
                padding-right: 10px;
            }

            /* Checkboxes */
            #modernCheckbox {
                color: #2D3748;
                font-size: 13px;
                spacing: 10px;
                padding: 8px;
            }

            #modernCheckbox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #CBD5E0;
                border-radius: 5px;
                background-color: #FFFFFF;
            }

            #modernCheckbox::indicator:checked {
                background-color: #667eea;
                border-color: #667eea;
                image: url(data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'><path d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/></svg>);
            }

            #modernCheckbox::indicator:hover {
                border-color: #667eea;
            }

            /* Progress Section */
            #progressFrame {
                background-color: #FFFFFF;
                border: 1px solid #E5E9F2;
                border-radius: 12px;
            }

            #statusLabel {
                color: #2D3748;
                font-size: 15px;
                font-weight: 600;
            }

            #currentFileLabel {
                color: #718096;
                font-size: 12px;
                font-style: italic;
            }

            #modernProgress {
                border: 2px solid #E5E9F2;
                border-radius: 17px;
                background-color: #F7FAFC;
                text-align: center;
                color: #2D3748;
                font-weight: bold;
            }

            #modernProgress::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
            }

            /* Tabs */
            #modernTabs::pane {
                border: 1px solid #E5E9F2;
                border-radius: 8px;
                background-color: #FFFFFF;
                top: -1px;
            }

            #modernTabs::tab-bar {
                left: 10px;
            }

            #modernTabs QTabBar::tab {
                background-color: #F7FAFC;
                border: 1px solid #E5E9F2;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 20px;
                margin-right: 2px;
                color: #718096;
                font-weight: 600;
                font-size: 13px;
            }

            #modernTabs QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #667eea;
                border-bottom: 3px solid #667eea;
            }

            #modernTabs QTabBar::tab:hover {
                background-color: #EDF2F7;
            }

            /* Toolbar Buttons */
            #toolbarButton {
                background-color: #F7FAFC;
                border: 1px solid #E5E9F2;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: 600;
                color: #4A5568;
            }

            #toolbarButton:hover {
                background-color: #EDF2F7;
                border-color: #667eea;
                color: #667eea;
            }

            /* Text Displays */
            #logText, #previewText {
                background-color: #FFFFFF;
                border: 1px solid #E5E9F2;
                border-radius: 8px;
                padding: 10px;
                color: #2D3748;
            }

            #statsDisplay {
                background-color: #FFFFFF;
                border: 1px solid #E5E9F2;
                border-radius: 8px;
                padding: 15px;
            }

            /* Table */
            #modernTable {
                background-color: #FFFFFF;
                border: 1px solid #E5E9F2;
                border-radius: 8px;
                gridline-color: #E5E9F2;
            }

            #modernTable::item {
                padding: 8px;
                color: #2D3748;
            }

            #modernTable::item:selected {
                background-color: #EBF4FF;
                color: #2C5282;
            }

            #modernTable::item:alternate {
                background-color: #F7FAFC;
            }

            QHeaderView::section {
                background-color: #F7FAFC;
                color: #4A5568;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #E5E9F2;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            /* Search Input */
            #searchInput {
                background-color: #FFFFFF;
                border: 2px solid #E5E9F2;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #2D3748;
            }

            #searchInput:focus {
                border-color: #667eea;
            }

            /* Status Bar */
            #modernStatusBar {
                background-color: #FFFFFF;
                border-top: 1px solid #E5E9F2;
                padding: 5px;
            }

            #statusMessage {
                color: #4A5568;
                font-size: 12px;
                padding: 5px;
            }

            #statusIndicator {
                color: #718096;
                font-size: 11px;
                padding: 5px 10px;
                margin: 0 2px;
                background-color: #F7FAFC;
                border-radius: 5px;
            }

            /* Scrollbars */
            QScrollBar:vertical {
                background-color: #F7FAFC;
                width: 12px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background-color: #CBD5E0;
                border-radius: 6px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #A0AEC0;
            }

            QScrollBar:horizontal {
                background-color: #F7FAFC;
                height: 12px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal {
                background-color: #CBD5E0;
                border-radius: 6px;
                min-width: 30px;
            }

            QScrollBar::handle:horizontal:hover {
                background-color: #A0AEC0;
            }

            QScrollBar::add-line, QScrollBar::sub-line {
                border: none;
                background: none;
            }

            /* Tooltips */
            QToolTip {
                background-color: #2D3748;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
            }
        """)

    def _apply_animations(self):
        """Apply smooth animations"""
        # Fade in animation for main window
        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        self.centralWidget().setGraphicsEffect(self.opacity_effect)

        self.fade_in = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(500)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self.fade_in.start()

    def _setup_connections(self):
        """Setup signal connections"""
        # Navigation buttons
        self.theme_btn.clicked.connect(self._toggle_theme)
        self.settings_btn.clicked.connect(self._show_settings)
        self.help_btn.clicked.connect(self._show_about)

        # Control buttons
        self.input_btn.clicked.connect(self._select_input)
        self.output_btn.clicked.connect(self._select_output)
        self.start_btn.clicked.connect(self._start_extraction)
        self.cancel_btn.clicked.connect(self._cancel_extraction)

        # Connect to logger
        qt_handler = self.logger_manager.get_qt_handler()
        qt_handler.log_signal.connect(self._on_log_message)

    def _toggle_theme(self):
        """Toggle between light and dark theme"""
        # This would toggle themes - for now just show message
        QtWidgets.QMessageBox.information(
            self, "Theme",
            "Theme switching feature - Light/Dark mode toggle"
        )

    def _select_input(self):
        """Select input directory"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Input Directory Containing PDF Files"
        )
        if folder:
            self.input_dir = Path(folder)
            self.input_lbl.setText(folder)

            # Count PDFs
            pdf_files = list(self.input_dir.glob("*.pdf"))
            self.pdf_count_lbl.setText(f"PDFs Found: {len(pdf_files)}")

            self._check_ready()

    def _select_output(self):
        """Select output directory"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Output Directory for Extracted References"
        )
        if folder:
            self.output_dir = Path(folder)
            self.output_lbl.setText(folder)
            self._check_ready()

    def _check_ready(self):
        """Check if ready to start"""
        ready = hasattr(self, 'input_dir') and hasattr(self, 'output_dir')
        self.start_btn.setEnabled(ready)

        if ready:
            pdf_files = list(self.input_dir.glob("*.pdf"))
            if pdf_files:
                self.status_icon.setText("✅")
                self.status_lbl.setText(f"Ready to process {len(pdf_files)} PDF file(s)")
            else:
                self.status_icon.setText("⚠️")
                self.status_lbl.setText("No PDF files found in input directory")
                self.start_btn.setEnabled(False)

    def _start_extraction(self):
        """Start extraction process"""
        # Get PDF files
        pdf_files = list(self.input_dir.glob("*.pdf"))
        if not pdf_files:
            QtWidgets.QMessageBox.warning(
                self, "No PDFs Found",
                "No PDF files found in the selected input directory."
            )
            return

        # Update UI
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.log_text.clear()
        self.preview_text.clear()
        self.progress_bar.setMaximum(len(pdf_files))
        self.progress_bar.setValue(0)
        self.status_icon.setText("⏳")
        self.status_lbl.setText("Processing...")

        # Build config
        format_text = self.format_combo.currentText()
        format_map = {"📄 BibTeX": "bibtex", "📋 RIS": "ris", "💼 JSON": "json", "📊 CSV": "csv"}

        config = {
            'default_export_format': format_map.get(format_text, "bibtex"),
            'citation_style': self.style_combo.currentText().lower(),
            'enable_api_enrichment': self.enrich_checkbox.isChecked(),
            'enable_ml_parsing': self.ml_checkbox.isChecked(),
            'enable_crossref': self.config.enable_crossref,
            'enable_doi_lookup': self.config.enable_doi_lookup,
            'db_path': self.config.db_path,
            'save_to_database': True
        }

        # Start worker
        worker = self.worker_manager.start_extraction(pdf_files, self.output_dir, config)

        # Connect worker signals
        worker.progress.connect(self._on_progress)
        worker.log_message.connect(self._on_log_message)
        worker.pdf_completed.connect(self._on_pdf_completed)
        worker.finished.connect(self._on_finished)
        worker.error.connect(self._on_error)

        self.logger.info(f"Started extraction of {len(pdf_files)} PDFs")

    def _cancel_extraction(self):
        """Cancel extraction"""
        reply = QtWidgets.QMessageBox.question(
            self, "Cancel Extraction",
            "Are you sure you want to cancel the current extraction process?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.worker_manager.cancel_extraction()
            self.status_icon.setText("⏹️")
            self.status_lbl.setText("Cancelling...")

    def _on_progress(self, current: int, total: int, status: str):
        """Handle progress update"""
        self.progress_bar.setValue(current)
        self.current_file_lbl.setText(status)
        self.pdfs_card.update_value(f"{current}/{total}")

    def _on_log_message(self, level: str, message: str):
        """Handle log message"""
        # Color-coded log messages
        colors = {
            "DEBUG": "#718096",
            "INFO": "#2D3748",
            "WARNING": "#ED8936",
            "ERROR": "#E53E3E",
            "CRITICAL": "#C53030"
        }
        color = colors.get(level, "#2D3748")

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f'<span style="color: {color};">[{timestamp}] [{level}] {message}</span>'

        self.log_text.appendHtml(formatted)
        self.status_msg.setText(message[:100])

    def _on_pdf_completed(self, pdf_name: str, ref_count: int, time: float):
        """Handle PDF completion"""
        self.log_text.appendHtml(
            f'<span style="color: #48BB78;">✓ Completed: {pdf_name} - {ref_count} references in {time:.2f}s</span>'
        )

    def _on_finished(self, stats: Dict[str, Any]):
        """Handle extraction finished"""
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_icon.setText("✅")
        self.status_lbl.setText("Extraction completed successfully!")
        self.current_file_lbl.setText("")

        # Update stats cards
        self.pdfs_card.update_value(str(stats['successful']))
        self.refs_card.update_value(str(stats['total_references']))
        self.time_card.update_value(f"{stats['elapsed_time']:.1f}s")
        self.speed_card.update_value(f"{stats['avg_time_per_pdf']:.1f}s/PDF")

        # Show completion dialog
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("✅ Extraction Complete")
        msg.setText(f"<h3>Successfully extracted {stats['total_references']} references!</h3>")
        msg.setInformativeText(
            f"<p><b>Processed:</b> {stats['successful']} / {stats['total_pdfs']} PDFs</p>"
            f"<p><b>Time:</b> {stats['elapsed_time']:.1f} seconds</p>"
            f"<p><b>Average Speed:</b> {stats['avg_time_per_pdf']:.1f}s per PDF</p>"
        )

        if self.auto_open_checkbox.isChecked():
            open_btn = msg.addButton("📂 Open Output Folder", QtWidgets.QMessageBox.ActionRole)
        msg.addButton(QtWidgets.QMessageBox.Ok)

        msg.exec()

        if self.auto_open_checkbox.isChecked() and msg.clickedButton() and msg.clickedButton().text() == "📂 Open Output Folder":
            import os
            import subprocess
            if os.name == 'nt':  # Windows
                os.startfile(self.output_dir)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.Popen(['open' if 'darwin' in os.sys.platform else 'xdg-open', self.output_dir])

        # Refresh database view
        self._refresh_database_view()

    def _on_error(self, error: str):
        """Handle error"""
        self.status_icon.setText("❌")
        self.status_lbl.setText("Error occurred")

        QtWidgets.QMessageBox.critical(
            self, "Error",
            f"An error occurred during extraction:\n\n{error}"
        )

        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

    def _view_reference(self, ref):
        """View detailed reference information"""
        # Create a detailed view dialog
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"Reference Details - {ref.title[:50]}...")
        dialog.setMinimumSize(700, 600)

        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Create scrollable area
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setSpacing(15)

        # Title
        title_label = QtWidgets.QLabel(f"<h2 style='color: #667eea;'>{ref.title}</h2>")
        title_label.setWordWrap(True)
        content_layout.addWidget(title_label)

        # Create info sections
        info_html = f"""
        <div style='background-color: #F7FAFC; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; margin: 10px 0;'>
            <p><b style='color: #4A5568;'>Authors:</b><br>{ref.authors}</p>
        </div>

        <div style='background-color: #F7FAFC; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; margin: 10px 0;'>
            <p><b style='color: #4A5568;'>Publication Details:</b><br>
            <b>Year:</b> {ref.year}<br>
            <b>Journal/Conference:</b> {ref.journal or 'N/A'}<br>
            <b>Volume:</b> {ref.volume or 'N/A'}<br>
            <b>Issue:</b> {ref.issue or 'N/A'}<br>
            <b>Pages:</b> {ref.pages or 'N/A'}</p>
        </div>

        <div style='background-color: #F7FAFC; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; margin: 10px 0;'>
            <p><b style='color: #4A5568;'>Identifiers:</b><br>
            <b>DOI:</b> {ref.doi or 'N/A'}<br>
            <b>Reference Number:</b> {ref.ref_number or 'N/A'}</p>
        </div>

        <div style='background-color: #F7FAFC; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; margin: 10px 0;'>
            <p><b style='color: #4A5568;'>Source:</b><br>
            <b>PDF File:</b> {ref.pdf_source}<br>
            <b>Citation Type:</b> {ref.citation_type}<br>
            <b>Confidence Score:</b> <span style='color: {'#48BB78' if ref.confidence_score >= 0.8 else '#ECC94B' if ref.confidence_score >= 0.6 else '#F56565'}; font-weight: bold;'>{ref.confidence_score:.2f}</span></p>
        </div>
        """

        if ref.abstract:
            info_html += f"""
            <div style='background-color: #F7FAFC; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; margin: 10px 0;'>
                <p><b style='color: #4A5568;'>Abstract:</b><br>{ref.abstract}</p>
            </div>
            """

        if ref.keywords:
            info_html += f"""
            <div style='background-color: #F7FAFC; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; margin: 10px 0;'>
                <p><b style='color: #4A5568;'>Keywords:</b><br>{ref.keywords}</p>
            </div>
            """

        info_text = QtWidgets.QTextEdit()
        info_text.setHtml(info_html)
        info_text.setReadOnly(True)
        info_text.setMinimumHeight(400)

        content_layout.addWidget(info_text)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Buttons at bottom
        button_layout = QtWidgets.QHBoxLayout()

        # Copy BibTeX button
        copy_btn = QtWidgets.QPushButton("📋 Copy BibTeX")
        copy_btn.setObjectName("toolbarButton")
        copy_btn.clicked.connect(lambda: self._copy_reference_bibtex(ref))

        # Open DOI button
        if ref.doi:
            doi_btn = QtWidgets.QPushButton("🔗 Open DOI")
            doi_btn.setObjectName("toolbarButton")
            doi_btn.clicked.connect(lambda: self._open_doi(ref.doi))
            button_layout.addWidget(doi_btn)

        # Close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setObjectName("toolbarButton")
        close_btn.clicked.connect(dialog.close)

        button_layout.addWidget(copy_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        # Show dialog
        dialog.exec()

    def _copy_reference_bibtex(self, ref):
        """Copy reference as BibTeX to clipboard"""
        from .exporter import BibTeXExporter
        from .reference_parser import ParsedReference

        # Convert database reference to ParsedReference
        parsed_ref = ParsedReference(
            ref_number=ref.ref_number or 0,
            raw_text="",
            authors=ref.authors.split(", ") if ref.authors else [],
            title=ref.title,
            year=ref.year,
            journal=ref.journal,
            volume=ref.volume,
            issue=ref.issue,
            pages=ref.pages,
            doi=ref.doi,
            citation_type=ref.citation_type,
            confidence=ref.confidence_score
        )

        exporter = BibTeXExporter()
        bibtex = exporter._to_bibtex(parsed_ref)

        # Copy to clipboard
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(bibtex)

        # Show confirmation
        QtWidgets.QMessageBox.information(
            self, "Copied",
            "BibTeX entry copied to clipboard!"
        )

    def _open_doi(self, doi):
        """Open DOI in web browser"""
        import webbrowser
        url = f"https://doi.org/{doi}"
        webbrowser.open(url)

        QtWidgets.QMessageBox.information(
            self, "Browser Opened",
            f"Opening DOI in your default browser:\n{url}"
        )

    def _refresh_database_view(self):
        """Refresh database table view"""
        refs = self.db.get_all_references(limit=100)
        self.db_table.setRowCount(len(refs))

        for row, ref in enumerate(refs):
            self.db_table.setItem(row, 0, QtWidgets.QTableWidgetItem(ref.title[:100]))
            self.db_table.setItem(row, 1, QtWidgets.QTableWidgetItem(ref.authors[:50]))
            self.db_table.setItem(row, 2, QtWidgets.QTableWidgetItem(ref.year))
            self.db_table.setItem(row, 3, QtWidgets.QTableWidgetItem(ref.journal[:50]))
            self.db_table.setItem(row, 4, QtWidgets.QTableWidgetItem(ref.doi))

            # Confidence with color
            conf_item = QtWidgets.QTableWidgetItem(f"{ref.confidence_score:.2f}")
            if ref.confidence_score >= 0.8:
                conf_item.setBackground(QtGui.QColor("#48BB78"))
            elif ref.confidence_score >= 0.6:
                conf_item.setBackground(QtGui.QColor("#ECC94B"))
            else:
                conf_item.setBackground(QtGui.QColor("#F56565"))
            conf_item.setForeground(QtGui.QColor("white"))
            self.db_table.setItem(row, 5, conf_item)

            # Actions button
            action_btn = QtWidgets.QPushButton("👁️ View")
            action_btn.setObjectName("toolbarButton")
            action_btn.setMaximumWidth(80)
            action_btn.setCursor(QtCore.Qt.PointingHandCursor)
            # Connect button to view function with reference data
            action_btn.clicked.connect(lambda checked, r=ref: self._view_reference(r))
            self.db_table.setCellWidget(row, 6, action_btn)

        self.record_count_lbl.setText(f"Total Records: {len(refs)}")

    def _export_database(self):
        """Export database to JSON"""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Database", "", "JSON Files (*.json)"
        )
        if path:
            success = self.db.export_to_json(Path(path))
            if success:
                QtWidgets.QMessageBox.information(
                    self, "Success",
                    f"✅ Database exported successfully to:\n{path}"
                )

    def _import_database(self):
        """Import database from JSON"""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Import Database", "", "JSON Files (*.json)"
        )
        if path:
            count = self.db.import_from_json(Path(path))
            QtWidgets.QMessageBox.information(
                self, "Success",
                f"✅ Successfully imported {count} references from:\n{path}"
            )
            self._refresh_database_view()

    def _show_settings(self):
        """Show settings dialog"""
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("⚙️ Settings")
        msg.setText("<h3>Configuration Settings</h3>")
        msg.setInformativeText(
            f"<p><b>Database:</b> {self.config.db_path}</p>"
            f"<p><b>Log Level:</b> {self.config.log_level}</p>"
            f"<p><b>Max Workers:</b> {self.config.max_workers}</p>"
            f"<p><b>API Rate Limit:</b> {self.config.api_rate_limit}/s</p>"
            f"<p><b>Theme:</b> {self.config.theme}</p>"
        )
        msg.exec()

    def _show_statistics(self):
        """Show statistics"""
        stats = self.db.get_statistics()

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; }}
                h2 {{ color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
                h3 {{ color: #4A5568; margin-top: 25px; }}
                .stat-box {{
                    background-color: #F7FAFC;
                    border-left: 4px solid #667eea;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                }}
                .stat-label {{ color: #718096; font-size: 12px; text-transform: uppercase; }}
                .stat-value {{ color: #2D3748; font-size: 24px; font-weight: bold; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{
                    background-color: #F7FAFC;
                    padding: 10px 15px;
                    margin: 5px 0;
                    border-radius: 5px;
                    border-left: 3px solid #667eea;
                }}
            </style>
        </head>
        <body>
            <h2>📊 Database Statistics</h2>

            <div class="stat-box">
                <div class="stat-label">Total References</div>
                <div class="stat-value">{stats.get('total_references', 0):,}</div>
            </div>

            <div class="stat-box">
                <div class="stat-label">Total PDFs Processed</div>
                <div class="stat-value">{stats.get('total_pdfs', 0):,}</div>
            </div>

            <div class="stat-box">
                <div class="stat-label">Average Confidence Score</div>
                <div class="stat-value">{stats.get('avg_confidence', 0):.2f}</div>
            </div>

            <h3>📅 References by Year</h3>
            <ul>
        """

        for year, count in list(stats.get('by_year', {}).items())[:10]:
            html += f"<li><b>{year}:</b> {count} references</li>"

        html += """
            </ul>

            <h3>📚 References by Type</h3>
            <ul>
        """

        for ref_type, count in stats.get('by_type', {}).items():
            html += f"<li><b>{ref_type}:</b> {count} references</li>"

        html += """
            </ul>
        </body>
        </html>
        """

        self.stats_text.setHtml(html)

    def _show_about(self):
        """Show about dialog"""
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("About IEEE Reference Extractor")
        msg.setText("<h2>📚 IEEE Reference Extractor</h2>")
        msg.setInformativeText(
            "<p><b>Version:</b> 3.0 Enterprise Edition</p>"
            "<p><b>Description:</b> Professional-grade reference extraction tool with ML-enhanced parsing and API enrichment.</p>"
            "<br>"
            "<p><b>✨ Key Features:</b></p>"
            "<ul style='margin-left: 20px;'>"
            "<li>🔍 Multi-column PDF text extraction</li>"
            "<li>🤖 ML-enhanced reference parsing</li>"
            "<li>🌐 CrossRef & DOI API integration</li>"
            "<li>📄 Multiple export formats (BibTeX, RIS, JSON, CSV)</li>"
            "<li>💾 SQLite database management</li>"
            "<li>📊 Real-time processing statistics</li>"
            "<li>🎨 Modern, professional UI</li>"
            "</ul>"
            "<br>"
            "<p style='color: #718096; font-size: 11px;'>© 2024 IEEE Reference Extractor Team</p>"
        )
        msg.setIconPixmap(QtGui.QPixmap())  # Add custom icon if available
        msg.exec()

    def _load_state(self):
        """Load previous session state"""
        # Load last used directories if saved
        if self.config.input_dir:
            self.input_dir = Path(self.config.input_dir)
            self.input_lbl.setText(self.config.input_dir)

        if self.config.output_dir:
            self.output_dir = Path(self.config.output_dir)
            self.output_lbl.setText(self.config.output_dir)

        self._check_ready()
        self._refresh_database_view()

    def closeEvent(self, event):
        """Handle window close"""
        # Save current directories
        if hasattr(self, 'input_dir'):
            self.config_manager.update(input_dir=str(self.input_dir))
        if hasattr(self, 'output_dir'):
            self.config_manager.update(output_dir=str(self.output_dir))

        self.config_manager.save()
        event.accept()
