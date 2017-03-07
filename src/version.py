# report-ng
# Copyright (c) 2017 Marcin Woloszyn (@hvqzao)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


if __name__ == '__main__':
    import datetime ; print datetime.datetime.ctime(datetime.datetime.now())

class Version(object):
    title = 'report-ng'
    long_title = 'Web application security assessment reporting tool'
    c = 'Copyright (C) 2014-2017 Marcin Woloszyn (@hvqzao)'
    #url = 'https://github.com/hvqzao/report-ng'
    url = ''
    #license = 'Distributed under GNU General Public License, Version 2, June 1991'
    license = ''
    about = '''
    Generate reports based on HP WebInspect, BurpSuite Pro scans,
    own custom data, knowledge base and Microsoft Office Word templates.
    '''
    version = '0.8.9'
    date = 'Tue Mar  7 19:50:56 2017'
    changelog = '''
    0.8.9 - Tue Mar  7 19:50:56 2017
    - added: if-not for non-finding elements: root (tested) and child (not-tested)
    
    0.8.8 - Tue Mar  7 13:56:31 2017
    - FIX: Premature KB cleanup prevented populating Summary descriptions fields

    0.8.7 - Mon Feb 27 14:32:29 2017
    - "Merge KB into Content" is now performed before report is generated.
    
    0.8.6 - Mon Feb 27 10:51:56 2017
    - FIX: crash when findings severity is present which is not on a template
    
    0.8.5 - Mon Feb 27 10:18:59 2017
    - FIX: crash at Merge KB into Content
    
    0.8.4 - Wed Feb 22 12:58:11 2017
    - FIX: Finding placeholders for given severities (eg. Best Practices) can
    now be removed from templates
    
    0.8.3 - Tue Feb 14 11:04:55 2017
    - added: Yamled edit now suports "Ctrl+A", it should now be possible to work
    with it using keyboard only
    
    0.8.2 - Fri Feb 10 21:14:03 2017
    - New: "Menu Tools / Switch to Yamled" - closes report-ng, starts Yamled

    0.8.1 - Tue Feb  7 14:24:30 2017
    - "If not exists" should now work for both Finding root and child nodes
    
    0.8.0 - Mon Feb  6 21:14:08 2017
    - "If not exists" handling added to Finding section (basic functionality)

    0.7.9 - Sat Feb  4 19:18:06 2017
    - New feature available from menu item added: Merge KB into Content

    0.7.8 - Mon Jun 27 15:39:34 2016
    - Improper input check
    
    0.7.7 - Mon May 16 15:39:02 2016
    - FIX: VIEWSTATE truncation should now work properly
    - Upgrade to Python 2.7.11 and upstream modules
    
    0.7.6 - Thu Apr  7 14:35:07 2016
    - FIX: making sure burp request/reponses are properly encoded

    0.7.5 - Thu Jan 14 11:00:04 2016
    - yamled: Ctrl+A will now start editing given cell and select all content
    - report-ng: content directory is now default location for saving generated content
    
    0.7.4 - Mon Nov 30 12:00:35 2015
    - FIX: Burp edge case issues
    
    0.7.3 - Mon Oct 26 15:59:34 2015
    - FIX: XML characters validation missing
    
    0.7.2 - Fri Jul 10 13:29:38 2015
    - If there will be no Finding.Summary.X, it will fallback to Finding.X value
    - Yamled sets bold for a value of first key in dictionary

    0.7.1 - Tue Jun 23 11:03:09 2015
    - FIX: Encoding handling issue
    
    0.7.0 - Mon May 18 10:57:28 2015
    - FIX: Temporary workaround for minor issue during report generation

    0.6.9 - Sun Apr 19 21:06:39 2015
    - Ability to include requests and responses from imported scan (slow and heavy!).

    0.6.8 - Thu Apr  9 15:27:37 2015
    - Minor code cleanups. Yamled still needs performance upgrade fixes.

    0.6.7 - Mon Mar  2 15:15:58 2015
    - It is now possible to import Occurrences from Burp's "Save (selected) items"
      right click popup menu action generated xml. This might be useful for adding
      earlier filtered items discovered during Intruder tests.

    0.6.6 - Tue Feb 17 12:03:30 2015
    - FIX: Yamled load on drag & drop should now work
    - FIX: Yamled crash on use of Escape should now be eliminated
    - Yamled tree view now allows use of Enter key to edit value of selected key
    - Yamled Ctrl+S save is now supported
    
    0.6.5 - Thu Feb  5 21:20:53 2015
    - FIX: Yamled infinite loop during file saving has been eliminated
    - FIX: Loaded data should now be properly structured
    - Yamled now supports file loading via drag & drop

    0.6.4 - Thu Feb  5 13:07:53 2015
    - FIX: Importing huge xml scans generated by Webinspect should now work properly
    - FIX: saving lists in Yamled of one item dicts should now be proper
    - Yamled will notify about unsaved changes
    - Yamled value edition can now be finished with Tab or Escape key
    - Minor fixes

    0.6.3 - Mon Dec 29 23:58:28 2014
    - Yamled add new node (currently only when selected node is parent to a list)
    
    0.6.2 - Mon Dec 29 19:50:06 2014
    - Yamled editing minor enhancements

    0.6.1 - Sun Dec 28 23:28:41 2014
    - Yamled values editing is now using multiline field
    
    0.6.0 - Fri Dec 26 21:05:43 2014
    - FIX: Multipart requests will now be shown as proper multiline content
    
    0.5.9 - Thu Dec 25 22:55:01 2014
    - FIX: Multipart requests data will now land in Finding.Occurrences.Post
    - FIX: Two cases for loading of manually created yaml file were fixed
    
    0.5.8 - Sun Nov 23 21:01:03 2014
    - Yamled button is now available for Content
    - Yamled saving scan is now possible
    - Yamled nodes deletion has been added
    - Yamled popup menu has been extended: Collapse All / Expand All
    
    0.5.7 - Fri Nov 21 07:28:04 2014
    - __EVENTVALIDATION is now shortened same way as __VIEWSTATE
    
    0.5.6 - Thu Nov 13 14:31:49 2014
    - FIX: params truncation handling bugfix
    
    0.5.5 - Fri Sep 26 13:09:41 2014
    - FIX: Burp scan imports issueBackground is now handled as optional field
    - FIX: Due to specific Burp extension, scan grouping is now name based as vuln_id became ambiguous
    
    0.5.4 - Thu Sep 25 20:24:39 2014
    - Finding summary counter and graphing are now using fallback count equal 1
    
    0.5.3 - Tue Sep 23 17:53:12 2014
    - FIX: Binary content (e.g. gif file HTTP response) in should now be handled properly
    - WebInspect and Burp scans first parameter is now Name, not Severity
    
    0.5.2 - Sun Sep 21 12:10:03 2014
    - Yamled node collapsing/expanding added
    - Yamled scrolling and content loading fixes

    0.5.1 - Fri Sep 19 21:14:32 2014
    - FIX: WebInspect scan import proper VulnerabilityID inputs handling
    - Yaml editor added (not yet functional)
    
    0.5.0 - Mon Sep 15 18:16:54 2014
    - All child windows are now screen centered
    - Gui module cleanup + new, experimental, yet unusable yamled module
    - Yamled wrapper and icon added

    0.4.9 - Fri Sep 12 23:55:55 2014
    - ViewState truncation now affects scan saving as well as merging into content
    - FIX: Always on top should now work everytime application starts

    0.4.8 - Fri Sep 12 22:04:57 2014
    - ASP and javax.faces ViewState truncation menu switch added (enabled by default)
    - Truncation now also affects scan preview textarea (for performance reasons)
    - FIX: wxpython 3.0 redirect stdio to window defaults set to False, True is now enforced
    - FIX: vulnparam highlighting GUI switch will now work as expected
    
    0.4.7 - Sun Aug 31 13:46:42 2014
    - Always on top menu switch added (enabled by default)
    - Usage help is now rendered as html
    
    0.4.6 - Tue Aug 26 22:32:28 2014
    - KB import from csv generated from Sharepoint filters few unwanted characters
    - cx_Freeze builder added to remediate pyinstaller's 10 second start lag on many systems
    
    0.4.5 - Sun Aug 24 21:17:17 2014
    - Switching view between json/yaml works now for KB as well
    - More verbose status bar when loading files
    - Minor template adjustment to be more in-line with current features
    - wxpython 2.8 upgraded to 3.0 for future use features
    
    0.4.4 - Wed Aug 20 18:41:37 2014
    - FIX: VulnParam highlighting has been fixed and should now be more accurate
    - if Finding.[Severity] placeholder contains only blank characters, it will be removed
    
    0.4.3 - Wed Aug 13 18:28:25 2014
    - FIX: Each conditional tag should now be handled, not only the first one
    - yaml/json saved files are now UTF-8 encoded by default
    - minor fix in KB CSV import
    
    0.4.2 - Mon Aug 11 18:44:01 2014
    - FIX: Switching off clean for templates missing Finding.Severity now works fine
    - Application now starts aligned to the right which is more convenient for drag & drop
    - Cleanup after saving report is now performed so another report could be produced without
      need for application restart
    - Redundant cleanups are now being avoided
    
    0.4.1 - Sat Jul 12 15:09:43 2014
    - FIX: KB entries are now correctly set for nested undefined findings content

    0.4.0 - Sat Jul 12 11:11:46 2014
    - Added: CVS imported KB now supports nesting (e.g. Summary.Description)
    
    0.3.9 - Fri Jul 11 20:08:34 2014
    - FIX: Plain text now correctly replaces tag content with multiple runs
    - FIX: Pseudohtml font size should now be correctly handled
    - FIX: clean=False multiple runs now join with no redundant blanks
    - Added: Finding placeholder now acts as a fallback when no findings of
      given severity are present
    
    0.3.8 - Thu Jul 10 17:57:17 2014
    - Added: Aliases support for Knowledge Base
    
    0.3.7 - Wed Jul  9 20:07:28 2014
    - FIX: CSV formatting issues

    0.3.6 - Tue Jul  8 19:41:20 2014
    - Added: Example request and response are now included in each finding
    - FIX: Rendering cleanup issue has been fixed
    
    0.3.5 - Mon Jul  7 21:31:18 2014
    - Added: Conditional tags handling in content below root
    - Added: Statusbar
    - Random Password Generator introduced
    - Added: KB might now be loaded from Excel CSV file
    - Added: Drag & drop status hints
    
    0.3.4 - Fri Jul  4 23:10:12 2014
    - FIX: Content refresh added after Scan merge to keep state consistency
    - FIX: Left templating elements are now cleaned up
    - FIX: Lack of value in yaml is now threated as empty string
    - Added: VulnParam highlighting now have a checkbox in View Menu
    
    0.3.3 - Thu Jul  3 22:08:40 2014
    - FIX: WebInspect scan import minor issue
    - Added: VulnParam highlighting in Finding.Occurrences.Location and Post
    
    0.3.2 - Wed Jul  2 21:55:48 2014
    - Added: Tools / Merge Scan into Content
    - Added: File / Save Content As
    - Added: VulnParam in occurrences of Burp/WebInspect scans
    
    0.3.1 - Sat Jun 28 20:23:14 2014
    - Findings.VolumeChart tag added
    - Pseudohtml tags change: r/red = red text, rw/redwhite = red highlight

    0.3.0 - Sat Jun 28 16:52:45 2014
    - HP WebInspect scan ~FullURL~ is now properly handled
    - changed way HP WebInspect scan Classification URLs are presented
    - content formatting fixes
    
    0.2.9 - Sat Jun 28 00:21:41 2014
    - added conditional root blocks in content
    - counter capability added to findings summary
    
    0.2.8 - Thu Jun 27 17:34:49 2014
    - minor formatting issues
    - added conditional blocks within findings
    
    0.2.7 - Sun May  4 23:02:01 2014
    - documentation updates
    
    0.2.6 - Fri May  2 16:13:22 2014
    - added: command-line support
    - added: License information
    
    0.2.5 - Mon Apr 28 02:11:00 2014
    - FIX: html/ihtml sections should now land correctly in summary table cells
    
    0.2.4 - Sat Apr 26 11:27:01 2014
    - added: Template structure preview

    0.2.3 - Thu Apr 24 22:12:09 2014
    - FIX: <img src="..."> is now relative to template file directory
    - html/ihtml sections are now more error proof
    - source code has been reorganized into smaller pieces
    - source has been cleaned up a bit

    0.2.2 - Mon Apr 21 03:01:05 2014
    - HP WebInspect and Burp Suite Pro scans are now supported
    - pseudo-html is now supported as an input for template
    - added: Changelog
    '''
    #'0.2.1 Sun Apr 13 21:17:13 2014'
    #'0.2.0 Sun Apr  6 20:03:13 2014'
    #'0.1.9 Sun Apr  6 12:47:31 2014'
    #'0.1.8 Sat Apr  5 19:06:10 2014'
    #'0.1.7 Fri Apr  4 23:41:16 2014'
    #'0.1.6 Sun Mar 23 14:01:58 2014'
    usage = '''
    # Web Application Security Assessment Reporting

    The idea behind is to speed up the preparation stage of penetration
    testing and dynamic scanning reports as well as make it more uniform.

    ## Basics

    Microsoft Office Word is being used to prepare report templates.
    HP WebInspect and BurpSuite Pro scan exports might be used as input
    data for the report as well.
    XML, Yaml and Json are used as input formats.
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

    Double click on given text area will popup the content on larger area.

    ## CLI Interface

    Command-line support has been added in order to allow bulk generation
    of report-files. Application currently supports one set of switches:
    
    -t template-file [-c content-file] [-k kb-file] [-s scan-file]
    -r report-file

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
    - Finding - finding template, it should include other Finding.* tags
      - Finding.Name
      - Finding.Severity - allowed: Critical, High, Medium, Low, Informational
        Best Practices

    Optional fields:
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

    It is recommended to arrange data in structures, e.g.:
    - Report.Name - paragraph
    - Report.Owner - span
    ...

    It is possible to prepare table templates as well, e.g.:
    - History - table row
    - History.Version - table column (or span within table column)
    - History.Date - table column
    ...
    It applies to both data and Finding structures.

    Conditionals

    Conditional blocks have been introduced to findings in the following ways:

    "if exists"
    - Surrounding template data within e.g. Finding.Critical?
      causes block to appear only for critical findings.
    - If finding includes some tag, e.g. Finding.Description, conditional
      block Finding.Description? could be added to the template. Content will
      only be rendered if finding have Finding.Description set. IMPORTANT:
      Make sure Conditional is created as block (multi-line). Once tested
      it can an attempt can be made to join it back to a single line.
      Block tag seen in Word "Developer Mode" have named closing tag.

    "if not exists"
    - if fining does not include some tag or its value is set to '',
      given block will be visible, otherwise it is removed.

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
    - plain text
    - Regular pseudo-html data: <html>...</html>
    - Inline pseudo-html data: <ihtml>...</ihtml> - keep in mind that it
      might have some limitations and it could cause problems.

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
    - <b>...</b> - bold
    - <i>...</i> - italic
    - <y>...</y> (or <yellow>...</yellow) - yellow highlight
    - <r>...</r> (or <red>...</red>) - red text
    - <rw>...</rw> (or <redwhite>...</redwhite>) - red highlight with white text
    - <a href="...">...</a> - link (remember to use scheme in url, e.g.
      http://)
    - <font [face="..."] [size="..."]>...</font> - font, no units just a numeric
      value

    ## Regular pseudo-html allowed tags

    All inline tags could be used. Additionally available are:
    - <ul><li>...</li>...</ul> - unnumbered list
    - <ol><li>...</li>...</ol> - numbered list
    - <xl>...</xl> - supplementary, indented only list item, e.g.:
      <ul><li>item</li><xl>item description</xl><li>...</li></ul>
    - <img src="..." [alt="..."] [width="..."] /> - image, no units for width,
      just a numerical value
    - <br/> - break line

    ## Scans

    HP WebInspect 10.1.177.0 and Burp Suite Pro 1.6beta2 / 1.6.01 were used
    during initial tests. To prepare source scan data within HP WebInspect, Export
    Scan Details (Full) with XML Export Format. For Burp use Report Selected
    Issues, select XML and pick Base64-encode requests and responses.
    '''
    #
    ### License
    #
    #GNU General Public License, Version 2, June 1991
