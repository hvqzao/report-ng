# Todo:

```
- Finding.Severity as optional
```

# For consideration:

```
- Evidence Highlight (e.g. Cookie)
- verify vulnparam behavior for more burp scans (cookies?)
- status messages
- status-related background debug window
- verify all xml node getparent ?= None
```

# Recent activity:

```
+ BUG: if Report.Key? is used more than once, only the first one is handled
+ BUG: (probably) utf-8 encoded content loaded as scan and merged + report causes
  non ascii conversion issue
+ Fix nasty bug in multiple runs formatting
+ Finding placeholders - if no findings - use as a fallback
+ Evidence Request Header
+ Evidence Response Header
+ Special case fix: sdt_remove/replace getparent = None handling
+ import csv knowledge base
+ random password / passphrase generator (rpg)
+ status bar
+ Conditionals in report content for empty values (below root)
+ Conditionals in report content for missing keys (below root)
+ bug: post scan_merge operation missing (~reload) -> no findings in report generated
+ replace sdt with child for unset yaml
+ yaml tag with no value at all (key: $) is None -> should be removed
+ add: pyinstaller --clean --assume y
+ Menu: Auto/Smart-Highlight off switch
+ Occurrence Get/Post VulnParam Highlighting
+ Occurrence VulnParam (Burp)
+ Occurrence VulnParam (Webinspect)
+ Merge Scan into Content
```
