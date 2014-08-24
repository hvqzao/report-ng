# Wasar
# Copyright (c) 2014 Marcin Woloszyn (@hvqzao)
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
    title = 'Wasar'
    long_title = 'Web Application Security Assessment Reporting'
    c = 'Copyright (C) 2014 Marcin Woloszyn (@hvqzao)'
    #url = 'https://github.com/hvqzao/wasar'
    url = ''
    #license = 'Distributed under GNU General Public License, Version 2, June 1991'
    license = ''
    about = '''
    Generate reports based on HP WebInspect, BurpSuite Pro scans,
    own custom data, knowledge base and Microsoft Office Word templates.
    '''
    version = '0.4.5'
    date = 'Sun Aug 24 21:17:17 2014'
    changelog = '''
    0.4.5 - Sun Aug 24 21:17:17 2014
    - Switching view between json/yaml works now for KB as well
    - More verbose status bar when loading files
    - Minor template adjustment to be more in-line with current features
    
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
    - Surrounding template data within e.g. Finding.Critical?
      causes block to appear only for critical findings.
    - If finding includes some tag, e.g. Finding.Description, conditional
      block Finding.Description? could be added to the template. Content will
      only be rendered if finding have Finding.Description set.

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
    during tests. To prepare source scan data within HP WebInspect, Export
    Scan Details (Full) with XML Export Format. For Burp use Report Selected
    Issues, select XML and pick Base64-encode requests and responses.
    '''
    #
    ### License
    #
    #GNU General Public License, Version 2, June 1991
