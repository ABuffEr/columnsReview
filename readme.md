# Columns Review

* Author: Alberto Buffolino, Łukasz Golonka, other contributors
* NVDA compatibility: 2019.3 and beyond

Columns Review is an add-on to enhance NVDA experience with lists.

Its features include:

* customizable actions on column header and/or content (available actions are read, copy, spell and show in browse mode);
* ability to cycle between columns in ten-by-ten intervals;
* simplified header management (mouse clicks);
* on-demand reading of relative current item position (i.e.: item 7 of 10);
* customizable gestures with or without numpad;
* "0 items" announcement when list is empty;
* top/bottom edge reporting via speech or beeps;
* say all support;
* report of selected items (amount and item names);
* list search (with item multiselection, if checked/supported).

## Gestures

Default keys for columns, headers and position are NVDA+control, but you can customize them from add-on settings (not "Input gestures" dialog!).

Note that your keyboard could have problems processing some key combinations, so try all add-on gestures and adjust them for better results.

See also add-on preferences for numpad mode, keyboard layout (without numpad), and the four available actions for columns.

* NVDA+control+digits from 1 to 0 (keyboard mode) or from 1 to 9 (numpad mode): by default, read the chosen column if pressed once, copy it if pressed twice;
* NVDA+control+numpadMinus (numpad mode): like NVDA+control+0 in keyboard mode, read or copy the 10th, 20th, etc column;
* NVDA+control+- (keyboard mode, EN-US layout): in a list with 10+ columns, change interval and process columns from 11 to 20, from 21 to 30, and so on (change last char according to your layout, from settings);
* NVDA+control+numpadPlus (numpad mode): like previous command;
* NVDA+control+enter (numpadEnter in numpad mode): open header manager;
* NVDA+control+delete (numpadDelete in numpad mode): read relative current item position (i.e.: item 7 of 10);
* Arrows and NVDA+tab (in empty list): repeat "0 items" message;
* NVDA+downArrow (desktop layout) or NVDA+a (laptop layout): start say all (this gesture depends on original one under "Input gestures"/"System caret");
* NVDA+shift+upArrow (desktop layout) or NVDA+shift+s (laptop layout): report amount and names of current selected list items (like previous command for customization);
* NVDA+control+f: open find dialog (not customizable);
* NVDA+f3: find next occurrence of previously entered text (not customizable);
* NVDA+shift+f3: find previous occurrence (not customizable).

## Support

This add-on provide a general support for more common lists (see below), and some specific applications. Main author (Alberto Buffolino) cannot guarantee compatibility/functionality for those applications he not uses, like Outlook and Windows Mail, but he'll be happy to collaborate with their users or accept a pull request for them (note: Outlook is covered now, but user reports are still welcome).

Following list types are supported:

* SysListView32;
* DirectUIHWND (present in 64-bit systems);
* WindowsForms10.SysListView32.* (applications that use .NET);
* multi-column treeview like as that presents in [RSSOwlnix][rss];
* Thunderbird messages table (thread-grouping supported);
* Outlook messages table (but list search is not recommended in thread view).

[rss]: https://github.com/ABuffEr/rssowlnixSupport

