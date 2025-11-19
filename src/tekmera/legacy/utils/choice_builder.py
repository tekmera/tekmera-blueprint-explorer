"""
Choice builder utility for consistent InquirerPy menu construction
"""

from typing import List, Optional, Union

from InquirerPy.separator import Separator

from .constants import MenuChoices, Symbols


class ChoiceBuilder:
    """
    Utility class for building consistent InquirerPy choice lists across the application.

    Provides methods to construct common menu patterns, navigation choices,
    and standardized separators for a consistent user experience.
    """

    def __init__(self):
        self.choices = []

    def add_choice(self, name: str, value: str, disabled: bool = False) -> "ChoiceBuilder":
        """
        Add a single choice to the list.

        Args:
            name: Display name for the choice
            value: Value to return when selected
            disabled: Whether the choice should be disabled

        Returns:
            Self for method chaining
        """
        choice = {"name": name, "value": value}
        if disabled:
            choice["disabled"] = True
        self.choices.append(choice)
        return self

    def add_choices(self, choices: List[dict]) -> "ChoiceBuilder":
        """
        Add multiple choices to the list.

        Args:
            choices: List of choice dictionaries

        Returns:
            Self for method chaining
        """
        self.choices.extend(choices)
        return self

    def add_separator(self, text: Optional[str] = None) -> "ChoiceBuilder":
        """
        Add a separator to the choice list.

        Args:
            text: Optional text for the separator

        Returns:
            Self for method chaining
        """
        if text:
            self.choices.append(Separator(text))
        else:
            self.choices.append(Separator())
        return self

    def add_back(self, enabled: bool = True) -> "ChoiceBuilder":
        """
        Add a standardized back navigation choice.

        Args:
            enabled: Whether the back option should be enabled

        Returns:
            Self for method chaining
        """
        if enabled:
            self.choices.append(MenuChoices.back_choice())
        return self

    def add_quit(self, enabled: bool = True) -> "ChoiceBuilder":
        """
        Add a standardized quit choice.

        Args:
            enabled: Whether the quit option should be enabled

        Returns:
            Self for method chaining
        """
        if enabled:
            self.choices.append(MenuChoices.quit_choice())
        return self

    def add_exit(self, enabled: bool = True) -> "ChoiceBuilder":
        """
        Add a standardized exit choice.

        Args:
            enabled: Whether the exit option should be enabled

        Returns:
            Self for method chaining
        """
        if enabled:
            self.choices.append(MenuChoices.exit_choice())
        return self

    def add_navigation_section(
        self, include_back: bool = True, include_quit: bool = True
    ) -> "ChoiceBuilder":
        """
        Add a complete navigation section with separator and standard choices.

        Args:
            include_back: Whether to include back navigation
            include_quit: Whether to include quit option

        Returns:
            Self for method chaining
        """
        if self.choices:  # Only add separator if there are existing choices
            self.add_separator()

        if include_back:
            self.add_back()
        if include_quit:
            self.add_quit()
        return self

    def add_blueprint_choices(
        self, blueprints: dict, show_module_count: bool = True
    ) -> "ChoiceBuilder":
        """
        Add choices for blueprint selection.

        Args:
            blueprints: Dictionary of blueprint data
            show_module_count: Whether to show module count in choice names

        Returns:
            Self for method chaining
        """
        for key, blueprint in blueprints.items():
            scenario_name = blueprint["scenario_name"]
            filename = blueprint["filename"]

            if show_module_count and "module_count" in blueprint:
                name = f"{scenario_name} ({filename}.json - {blueprint['module_count']} modules)"
            else:
                name = f"{scenario_name} ({filename}.json)"

            self.add_choice(name, key)
        return self

    def add_search_type_choices(self) -> "ChoiceBuilder":
        """
        Add standard search type choices for blueprint analysis.

        Returns:
            Self for method chaining
        """
        search_choices = [
            {"name": f"{Symbols.SEARCH} Field Search (DE: fields)", "value": "field_search"},
            {"name": f"{Symbols.MODULE} Module Type Search", "value": "module_search"},
            {"name": f"{Symbols.FILE} Text Search", "value": "text_search"},
            {"name": f"{Symbols.CHART} Field Usage Rankings", "value": "field_rankings"},
            {"name": f"{Symbols.CONNECTION} Connection Analysis", "value": "connections"},
        ]
        return self.add_choices(search_choices)

    def add_analysis_choices(self) -> "ChoiceBuilder":
        """
        Add standard analysis choices for blueprint operations.

        Returns:
            Self for method chaining
        """
        analysis_choices = [
            {"name": f"{Symbols.CHART} Generate Analysis Report", "value": "generate_report"},
            {"name": f"{Symbols.SEARCH} Cross-Blueprint Search", "value": "search"},
            {"name": f"{Symbols.MODULE} Module Statistics", "value": "module_stats"},
            {"name": f"{Symbols.CONNECTION} Connection Analysis", "value": "connections"},
        ]
        return self.add_choices(analysis_choices)

    def add_pagination_choices(
        self, current_page: int, total_pages: int, show_jump: bool = True
    ) -> "ChoiceBuilder":
        """
        Add pagination navigation choices.

        Args:
            current_page: Current page number (0-indexed)
            total_pages: Total number of pages
            show_jump: Whether to include jump-to-page option

        Returns:
            Self for method chaining
        """
        # Next page
        if current_page < total_pages - 1:
            self.add_choice(f"{Symbols.ARROW_RIGHT} Next page", "next")

        # Previous page
        if current_page > 0:
            self.add_choice(f"{Symbols.ARROW_LEFT} Previous page", "prev")

        # Jump to specific page
        if show_jump and total_pages > 2:
            self.add_choice(f"{Symbols.SEARCH} Jump to page", "jump")

        # Done viewing
        self.add_choice(f"{Symbols.CHECK_MARK} Done viewing", "done")
        return self

    def add_boolean_choices(
        self, true_label: str = "Yes", false_label: str = "No"
    ) -> "ChoiceBuilder":
        """
        Add yes/no boolean choices.

        Args:
            true_label: Label for true/yes option
            false_label: Label for false/no option

        Returns:
            Self for method chaining
        """
        self.choices.extend(
            [{"name": true_label, "value": True}, {"name": false_label, "value": False}]
        )
        return self

    def add_numbered_choices(self, items: List[str], start_index: int = 1) -> "ChoiceBuilder":
        """
        Add numbered choices from a list of items.

        Args:
            items: List of items to convert to numbered choices
            start_index: Starting number for the choices

        Returns:
            Self for method chaining
        """
        for i, item in enumerate(items, start_index):
            self.add_choice(f"{i}. {item}", item)
        return self

    def clear(self) -> "ChoiceBuilder":
        """
        Clear all choices from the builder.

        Returns:
            Self for method chaining
        """
        self.choices = []
        return self

    def build(self) -> List[Union[dict, Separator]]:
        """
        Build and return the final choices list.

        Returns:
            List of choices ready for use with InquirerPy
        """
        return self.choices.copy()

    def build_and_clear(self) -> List[Union[dict, Separator]]:
        """
        Build the choices list and clear the builder for reuse.

        Returns:
            List of choices ready for use with InquirerPy
        """
        choices = self.build()
        self.clear()
        return choices

    @classmethod
    def create(cls) -> "ChoiceBuilder":
        """
        Create a new ChoiceBuilder instance for fluent method chaining.

        Returns:
            New ChoiceBuilder instance
        """
        return cls()

    @classmethod
    def simple_menu(cls, choices: List[tuple], include_navigation: bool = True) -> List[dict]:
        """
        Create a simple menu from a list of (name, value) tuples.

        Args:
            choices: List of (name, value) tuples
            include_navigation: Whether to include back/quit navigation

        Returns:
            Complete choices list ready for InquirerPy
        """
        builder = cls()
        for name, value in choices:
            builder.add_choice(name, value)

        if include_navigation:
            builder.add_navigation_section()

        return builder.build()

    @classmethod
    def blueprint_menu(cls, blueprints: dict, include_navigation: bool = True) -> List[dict]:
        """
        Create a blueprint selection menu.

        Args:
            blueprints: Dictionary of blueprint data
            include_navigation: Whether to include back/quit navigation

        Returns:
            Complete choices list ready for InquirerPy
        """
        builder = cls().add_blueprint_choices(blueprints)

        if include_navigation:
            builder.add_navigation_section()

        return builder.build()

    @classmethod
    def search_menu(cls, include_navigation: bool = True) -> List[dict]:
        """
        Create a standard search menu.

        Args:
            include_navigation: Whether to include back/quit navigation

        Returns:
            Complete choices list ready for InquirerPy
        """
        builder = cls().add_search_type_choices()

        if include_navigation:
            builder.add_navigation_section()

        return builder.build()

    @classmethod
    def analysis_menu(cls, include_navigation: bool = True) -> List[dict]:
        """
        Create a standard analysis menu.

        Args:
            include_navigation: Whether to include back/quit navigation

        Returns:
            Complete choices list ready for InquirerPy
        """
        builder = cls().add_analysis_choices()

        if include_navigation:
            builder.add_navigation_section()

        return builder.build()
