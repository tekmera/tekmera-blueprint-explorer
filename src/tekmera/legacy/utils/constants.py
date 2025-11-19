"""
Centralized constants for UI messages, styling, and configuration
"""


# Rich console color styles
class Colors:
    """Rich console color constants for consistent styling across the application."""

    # Basic colors
    RED = "[red]"
    GREEN = "[green]"
    YELLOW = "[yellow]"
    BLUE = "[blue]"
    CYAN = "[cyan]"
    MAGENTA = "[magenta]"
    WHITE = "[white]"
    DIM = "[dim]"

    # Semantic colors
    ERROR = "[red]"
    SUCCESS = "[green]"
    WARNING = "[yellow]"
    INFO = "[blue]"
    HIGHLIGHT = "[bold yellow]"
    MUTED = "[dim]"

    # UI element colors
    TITLE = "[bold blue]"
    SUBTITLE = "[dim]"
    HEADER = "[bold cyan]"
    ACCENT = "[cyan]"

    # Status colors
    COMPLETED = "[green]"
    IN_PROGRESS = "[yellow]"
    PENDING = "[dim]"
    FAILED = "[red]"


class Messages:
    """Centralized UI messages for consistent text across the application."""

    # Common actions
    PRESS_ENTER = "Press Enter to continue..."
    LOADING = "Loading..."
    PLEASE_WAIT = "Please wait..."

    # Navigation
    BACK = "← Back"
    QUIT = "❌ Quit"
    EXIT = "❌ Exit"
    CONTINUE = "Continue"
    CANCEL = "Cancel"

    # Status messages
    SUCCESS_LOADED = "✅ Loaded successfully"
    SUCCESS_COMPLETED = "✅ Completed successfully"
    WARNING_NO_RESULTS = "⚠️ No results found"
    ERROR_LOADING = "❌ Error loading"
    ERROR_NOT_FOUND = "❌ Not found"

    # Blueprint-specific messages
    BLUEPRINTS_LOADING = "📂 Loading blueprints (including subfolders)..."
    BLUEPRINTS_LOADED = "✅ Loaded {count} blueprint(s) from directory tree"
    NO_BLUEPRINTS_FOUND = "⚠️ No blueprint files found in directory"
    BLUEPRINT_LOAD_ERROR = "❌ Could not load {filename}: {error}"

    # Search messages
    SEARCHING = "🔍 Searching..."
    SEARCH_RESULTS = "Found {count} result(s) for '{term}'"
    NO_SEARCH_RESULTS = "No results found for '{term}'"

    # Analysis messages
    ANALYZING = "📊 Analyzing blueprints..."
    ANALYSIS_COMPLETE = "✅ Analysis complete"

    # Interactive prompts
    SELECT_OPTION = "Select an option:"
    ENTER_TEXT = "Enter text:"
    CONFIRM_ACTION = "Are you sure?"
    CONFIRM_EXIT = "Are you sure you want to exit?"


class Symbols:
    """Unicode symbols and emoji for consistent UI elements."""

    # Navigation symbols
    ARROW_RIGHT = "➡️"
    ARROW_LEFT = "⬅️"
    ARROW_UP = "⬆️"
    ARROW_DOWN = "⬇️"

    # Status symbols
    CHECK_MARK = "✅"
    CROSS_MARK = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"

    # Action symbols
    SEARCH = "🔍"
    FOLDER = "📂"
    FILE = "📄"
    GEAR = "⚙️"
    CHART = "📊"

    # Menu symbols
    BULLET = "•"
    SEPARATOR = "─"
    DOUBLE_SEPARATOR = "═"

    # Blueprint-specific symbols
    MODULE = "🔧"
    FLOW = "🔄"
    CONNECTION = "🔗"
    BRANCH = "🔀"
    FINISH = "🏁"


class Settings:
    """Application-wide settings and configuration constants."""

    # Pagination settings
    DEFAULT_PAGE_SIZE = 20
    MODULES_PER_PAGE = 15
    SEARCH_RESULTS_PER_PAGE = 20

    # Display limits
    MAX_PREVIEW_LENGTH = 60
    MAX_CONTEXT_LENGTH = 100
    MAX_TABLE_CELL_WIDTH = 40

    # File patterns
    BLUEPRINT_PATTERN = "*.json"

    # Timeouts (in seconds)
    DEFAULT_TIMEOUT = 30
    SEARCH_TIMEOUT = 60

    # Feature flags
    ENABLE_DEBUG_MODE = False
    ENABLE_VERBOSE_LOGGING = False


class MenuChoices:
    """Standard menu choice structures for consistent menu building."""

    @staticmethod
    def back_choice() -> dict:
        """Standard back navigation choice."""
        return {"name": Messages.BACK, "value": "back"}

    @staticmethod
    def quit_choice() -> dict:
        """Standard quit choice."""
        return {"name": Messages.QUIT, "value": "quit"}

    @staticmethod
    def exit_choice() -> dict:
        """Standard exit choice."""
        return {"name": Messages.EXIT, "value": "exit"}

    @staticmethod
    def separator() -> object:
        """Standard menu separator."""
        from InquirerPy.separator import Separator

        return Separator()

    @staticmethod
    def navigation_choices(include_back: bool = True, include_quit: bool = True) -> list:
        """Standard navigation choices for menus."""
        choices = []
        if include_back:
            choices.append(MenuChoices.back_choice())
        if include_quit:
            choices.append(MenuChoices.quit_choice())
        return choices


class ErrorMessages:
    """Centralized error messages for consistent error handling."""

    # File system errors
    FILE_NOT_FOUND = "File not found: {path}"
    DIRECTORY_NOT_FOUND = "Directory not found: {path}"
    PERMISSION_DENIED = "Permission denied: {path}"

    # Blueprint errors
    INVALID_JSON = "Invalid JSON in file: {filename}"
    BLUEPRINT_PARSE_ERROR = "Error parsing blueprint: {error}"
    NO_BLUEPRINTS = "No blueprint files found in directory"

    # Search errors
    SEARCH_FAILED = "Search operation failed: {error}"
    INVALID_SEARCH_TERM = "Invalid search term: {term}"

    # Analysis errors
    ANALYSIS_FAILED = "Analysis failed: {error}"
    MODULE_PARSE_ERROR = "Error parsing modules: {error}"

    # License errors
    INVALID_LICENSE = "Invalid license key"
    LICENSE_EXPIRED = "License has expired"
    PREMIUM_REQUIRED = "Premium license required for this feature"


class SuccessMessages:
    """Centralized success messages for positive feedback."""

    # General operations
    OPERATION_COMPLETE = "Operation completed successfully"
    SAVE_COMPLETE = "Saved successfully"
    EXPORT_COMPLETE = "Export completed successfully"

    # Blueprint operations
    BLUEPRINTS_LOADED = "Successfully loaded {count} blueprints"
    ANALYSIS_COMPLETE = "Blueprint analysis completed successfully"

    # Search operations
    SEARCH_COMPLETE = "Search completed - found {count} results"

    # Configuration
    CONFIG_SAVED = "Configuration saved successfully"
    LICENSE_ACTIVATED = "License activated successfully"


# Formatting templates
class Templates:
    """Template strings for consistent formatting."""

    # Progress indicators
    PROGRESS = "Progress: {current}/{total} ({percent}%)"
    LOADING_SPINNER = "Loading {item}..."

    # Statistics
    STATS_SUMMARY = "Total: {total} | Success: {success} | Errors: {errors}"

    # File information
    FILE_INFO = "{name} ({size} bytes, modified {date})"

    # Search results
    SEARCH_RESULT_COUNT = "Found {count} result(s) for '{term}'"
    SEARCH_RESULT_ITEM = "{index}. {title} - {description}"

    # Blueprint information
    BLUEPRINT_SUMMARY = "{name} - {modules} modules, {connections} connections"
    MODULE_SUMMARY = "Module {id}: {type} ({status})"
