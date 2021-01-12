# report-ng - Web application security assessment reporting tool

The idea behind is to speed up the preparation stage of penetration
testing and automated scan reports as well as make it more uniform.

Developed with Python 2.7 on Windows. Code does not contain tests,
but application itself has proven its value in production use for
over two years now.

## Download

https://github.com/hvqzao/report-ng/releases/download/report-ng-0.9.9/report-ng-0.9.9.zip

## Demo videos

Watch it in action on Youtube:
https://www.youtube.com/watch?v=F6F4648hj2c&t=4m54s

Merging scans:
https://www.youtube.com/watch?v=k0O7YE93Vdk

report-ng in action:
![report-ng](https://cloud.githubusercontent.com/assets/4956006/9931996/a2a05a92-5d40-11e5-8043-3e412563498e.png)

built-in yaml editor:
![yamled](https://cloud.githubusercontent.com/assets/4956006/9932323/47facdea-5d43-11e5-99e9-619bcec548c6.png)

## Basics

Microsoft Office Word is being used to prepare report templates.
HP WebInspect and BurpSuite Pro scan exports might be used as input
data for the report as well.
XML and Yaml or Json are used interchangeably as input formats.
Report in Openxml format is the final product of this application.

Error traceback is on. If you will work with templating and wont stick
to the rules presented below, you will very likely encounter it.

## GUI Interface

Main application window contains four fields that act as an input
(drag & drop is supported):
- Template - Word report template
- Content - additional data that should be automatically propagated
  to the report
- Scan - HP WebInspect / Burp Suite Pro scan
- Knowledge base - knowledge base that could be used to reinforce
  final report customization
- Nmap scan - parse XML output files from Nmap scans and include them
  in the report

Double click on given text area will popup the content on larger area.

## CLI Interface

Command-line support has been added in order to allow bulk generation
of report-files. Application currently supports one set of switches:

```
-t template-file [-c content-file] [-k kb-file] [-s scan-file] [-n nmap-file]
-r report-file [-o output-content-file]
```

Example use:

```
python report-ng.py -t examples/example-2-scan-report-template.xml -c examples/example-2-content.yaml -k examples/example-2-kb.yaml -s examples/example-2-scan-export-Burp.xml -r examples/\!.xml -o examples/\!.yaml
```

## Word Template Preparation

This application was tested with Office 2010 Word documents saved with
Word XML Document format.

To prepare a template Developer tab must be enabled on Word's Ribbon.
Rich Text Content Control on Developer tab is used to mark parts that
should be used for templating. All Rich Text Controls in order to be
properly recognized must have Title property set using Properties.
Design Mode is also handy.

Before I start with templating, few introductionary words: Word document
itself is organized in an xml structure which more or less sticks to the
HTML layout principles. There are paragraphs (p), inline text (run ~ span),
tables, table rows (tr), table row columns (tc) and others. When content
is marked using Rich Text Content Control it gets encapsulated. So when
you encapsulate a whole line - it will work as paragraph, part of inline
text - will work as a span etc. When during templating you will use multi
line content, it will be splitted and added in multiple tags. Therefore,
one should keep in mind that while paragraphs will work as expected, span
blocks will just be contatenated. Margin settings for paragraphs will be
propagated across each line of template content. Run parent might be run,
paragraph or another element.

I strongly advise to prepare your template using method of small steps.
If you encounter some unexpected error, you will be able to revert back
easily. Also take a look at Tools / Template structure preview wchich
should aid you during some issues analysis.

The following titles are reserved for the purpose of automated template
population:

Required fields:
```
- Finding - finding template, it should include other Finding.* tags
  - Finding.Name
  - Finding.Severity - allowed: Critical, High, Medium, Low, Informational
    Best Practices
```

Optional fields:
```
- Finding.* - other fields
- Findings.Chart - chart with all findings will be filled automatically
- Findings.VolumeChart - auto chart listing finding occurrences count
- Findings.Critical - placeholder for critical findings
- Findings.High
- Findings.Medium
- Findings.Low
- Findings.Informational
- Findings.BestPractices
- Summary.Critical - must be a row
- Summary.Critical.Finding - will be filled with finding name
- Summary.Critical.* - optional fields, will be put in finding template
- Summary.High
- Summary.High.Finding
- Summary.High.*
- Summary.Medium
- Summary.Medium.Finding
- Summary.Medium.*
- Summary.Low
- Summary.Low.Finding
- Summary.Low.*
- Summary.Informational
- Summary.Informational.Finding
- Summary.Informational.*
- Summary.BestPractices
- Summary.BestPractices.Finding
- Summary.BestPractices.*
- *.*.*
- *.*
- *
```

It is recommended to arrange data in structures, e.g.:
```
- Report.Name - paragraph
- Report.Owner - span
...
```

It is possible to prepare table templates as well, e.g.:
```
- History - table row
- History.Version - table column (or span within table column)
- History.Date - table column
...
```
It applies to both data and Finding structures.

Conditionals

Conditional blocks have been introduced to findings in the following ways:
```
- Surrounding template data within e.g. Finding.Critical?
  causes block to appear only for critical findings.
- If finding includes some tag, e.g. Finding.Description, conditional
  block Finding.Description? could be added to the template. Content will
  only be rendered if finding have Finding.Description set.
```

It is now also possible to add root conditional blocks for content itself.
Example use would be e.g. adding Pentest? conditional block and few tags,
like Pentest.Name, Pentest.Version etc. If at least one Pentest.* will
be present and filled, block will be left, otherwise it will be removed
from generated report.

Counters

When needed, summary.[finding].property# counter could be added to show
lists volume. 

## Content and Knowledge Base preparation

Content could be provided in yaml or json format. Values could be one of
three kinds:
```
- plain text
- Regular pseudo-html data: <html>...</html>
- Inline pseudo-html data: <ihtml>...</ihtml> - keep in mind that it
  might have some limitations and it could cause problems.
```

Additionally, Knowledge Base file could be also used. It should basically
look like findings section of content. Name and Severity fields are mandatory,
all other are optional. If content will not provide appropiate value for
given section, it will be taken from knowlege base, if such section will be
available there.

Knowledge Base might be also imported from Excel CSV file. "Vulnerability
Name" column will be threated as Finding Name. Severity column is mandatory.
Optional Aliases column is newline separated list of finding names. If
finding name listed in aliases column will be present in the report and it
will be missing dedicated Knowledge Base entry - such will work as a fallback.
For fallback finding names listed in aliases column finding severity is being
ignored.

## Inline pseudo-html allowed tags

Following tags are available:
```
- <b>...</b> - bold
- <i>...</i> - italic
- <y>...</y> (or <yellow>...</yellow) - yellow highlight
- <r>...</r> (or <red>...</red>) - red text
- <rw>...</rw> (or <redwhite>...</redwhite>) - red highlight with white text
- <a href="...">...</a> - link (remember to use scheme in url, e.g.
  http://)
- <font [face="..."] [size="..."]>...</font> - font, no units just a numeric
  value
```

## Regular pseudo-html allowed tags

All inline tags could be used. Additionally available are:
```
- <ul><li>...</li>...</ul> - unnumbered list
- <ol><li>...</li>...</ol> - numbered list
- <xl>...</xl> - supplementary, indented only list item, e.g.:
  <ul><li>item</li><xl>item description</xl><li>...</li></ul>
- <img src="..." [alt="..."] [width="..."] /> - image, no units for width,
  just a numerical value
- <br/> - break line
```

## Scans

HP WebInspect 10.1.177.0 and Burp Suite Pro 1.6beta2 / 1.6.01 were used
during initial tests. To prepare source scan data within HP WebInspect, Export
Scan Details (Full) with XML Export Format. For Burp use Report Selected
Issues, select XML and pick Base64-encode requests and responses.

At the time of writing, everything works smoothly with HP WebInspect 10.50,
BurpSuite Pro 1.7.19 and Microsoft Office 2013. No modifications were
necessary.

## License

[GNU General Public License, Version 2, June 1991](http://www.gnu.org/licenses/gpl-2.0-standalone.html)
