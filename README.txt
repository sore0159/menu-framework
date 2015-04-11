Python Screen-based menu framework

An attempt to create a faux 'event-driven' user interface framework for use with python command line games.

Abstract "screen" classes form the meat of the work: easily subclassed handlers that parse events and define 'triggers'.  Three basic types of screens subclass examples are used in this project: Basic, Special, and Decorative.

Decorative screens are non-interactive: they exist only to provide background for other screens that come after them.

Special screens are set up to not have primary displays: mainly quick subchoice handlers for other menus.  They parse a series of events, do one job, then die.

Basic screens are the primary menus and the 'game' itself.

Uses cPickle for persistence, raw_input for user input, and formatted print for output.
