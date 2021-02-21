#!/usr/bin/env python3

""" 
Preproc.py - a Pandoc preprocessor for jamesmaye.co.uk

Script assumes it is run from the directory containing the copied markdown
files to be edited"
"""

import os 
import re


# --- File management functions ---

def open_file(file_name):
    """Open file in read mode"""    
    md_file = open(file_name, 'r')
    return md_file.read()




def save_file(target_directory, file_name, file_contents):
    """Open new file in write mode, write contents and close file
    
    Parameters:
     -  target_directory (string)
     -  file_name (string)
     -  file_contents (string)
    
    Side effects: 
     -  creates/overwrites file at specified location
    """    
    new_path = '{}/{}'.format(target_directory, file_name)
    new_file = open(new_path, 'w')
    new_file.write(file_contents)
    new_file.close


def fix_filename(file):
    """Remove any spaces from file name, replace with hyphens, make lowercase"""
    return file.replace(' ', '-').lower()


def make_folder(folder_paths):
    """Takes list of folder paths and creates folders if not existing"""
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


 
# --- Text Processing Functions---

def remove_H1(text):
    """Remove first line H1 header to be replaced by pandoc-generated header
    
       Only removes header if at start of document, leaves other H1 headers
       Defines H1 by markdown ATX-style (i.e. '# Header')
       Setext-style headers not supported.
    """
    
    new_text = re.sub("^#\s.*\n", "", text) 
               # Regex: match start of doc, single #, space, text, one newline
    return(new_text)




def fix_intralinks(text):
    """ Change Bear intranote links [[/example]] to Pandoc-compatible 
        format [example]. 
    
        Pandoc handles any spaces or apostrophes itself so do this
        before changing the wikilinks which need spaces removed
    """
    
    intra_linked_text = re.sub(r"\[\[\/(.*?)\]\]", r"[\1]", text)
    return(intra_linked_text)
    



def fix_wikilinks(text):
    """Change [[Wiki Links]] to markdown [Wiki Links](wiki-links)
       with surrounding custom <span> class to allow custom styling
       of intrawebsite links.
    """
    
    linked_text = re.sub(r'\[\[(.*?)\]\]', r"<span class='JM-link'>[\1](\1)</span>", text)
        # Matches [[wiklinks including spaces]], takes text within
        # brackets as group 1
        # Then replaces with [group 1](group 1)

    hyphen_linked_text =  re.sub(r"(\]\(.*?\))", 
        lambda m: m.group(1).replace(" ", "-").lower(), linked_text)
    # Remove spaces from these links, replace with hyphens
    # and make url lowercase
        # Regex: all one group so all are included in the lambda fn
        # (     - start of group 1
        # \]\(  - matches end of link text and start of link url bracket
        #         (backslashes used to escape brackets)
        # .*?   - matches any text within the url link bracket
        # \)    - matches closing url link bracket
        # )     - end of group 1
    
    return(hyphen_linked_text)




# --- Sidenotes ---

def create_sidenotes(text):
    sidenote_keys = re.findall(r"""[^:] # single character NOT colon
                                   \[\^ # open bracket and caret
                                   ([A-Za-z0-9 -]+) # capture group 
                                   \][^:] # close bracket + char NOT colon
                                   """, text, re.VERBOSE)
                    # capture group: sidenote key: 
                    # at least 1 alphanum, space or dash char
    if sidenote_keys:
        for key in sidenote_keys:
            regex_sidenote = r"\[\^{0}\]:\s*(.*?):\s*\[\^{0}\]".format(key)
            sidenote_text = re.findall(regex_sidenote, text, re.DOTALL)
            if sidenote_text:
                html = ('<label for="{0}" '
                'class="margin-toggle sidenote-number">'
                '</label><input type="checkbox" id="{0}" '
                'class="margin-toggle"/><span class="sidenote">'
                '{1}</span>'.format(key, sidenote_text[0]))
                
                # find the specific sidenote identifier denoting 
                # position in the text:
                regex_sidenote_pos = (r"([^:])" # NOT colon = text outside 
                            # of sidenote, so captures to be kept
                            "\[\^" # open bracket and caret
                            "{0}" # sidenote key
                           "\]([^:])".format(key)) # close bracket, close group
                           # then NOT colon i.e. return of body text
                
                # substitute sidenote identifier for sidenote text + 
                # surrounding HTML markup
                text = re.sub(regex_sidenote_pos, r"\1{}\2".format(html), text)
                
                # remove original markdown sidenote text
                text = re.sub(r"\[\^{0}\]:\s.*?:\[\^{0}\]".format(key), "", text, re.DOTALL)
            else:
                print('sidenote keys not matching!')
    return(text)
            




# --- Tags-specific functions ---

def extract_title(file, text):
    # Attempts to extract title from YAML block for use as key in tags dict
    # If fails returns filename and extension as backup
    title_list = re.findall(r'\ntitle:\s(.*?)\n', text)
    if title_list:
        return(title_list[0])
    else:
        return(file)




def extract_tags(text):
    tags_string = re.findall(r'\ntags:\s\[(.*?)\]', text)
    if tags_string:       # Catches noneType errors if no tags in YAML        
        tags_list = tags_string[0].split(', ')
        return(tags_list)
    else:
        return(['untagged'])
        



def update_tags_dict(dict, file, text):
    """Creates dictionary with each tag a key and each value a list of
       pages containing that tag, each containing a tuple of (title, filename).
       If unable to extract page title, falls back to filename
    """
    
    title = extract_title(file, text)
    tags = extract_tags(text)
    
    # di
    file_tuple = (title, file[:-3])  # Removes the '.md'
    for tag in tags:
        if tag in dict:
            dict[tag].append(file_tuple)
        else:
            dict[tag] = [file_tuple]
    return(dict)
        



def create_tag_pages(target_directory, tags_dict):
    """Creates a .md file for each tag key in dictionary & populates
       with markdown list of links to pages containing those tags
    
       Parameters:
        - target_directory : string e.g. 'folder/subfolder'
        - tags_dict : dict with nested list 
                      e.g. {'tag1': ['pageA', 'pageB']}
       Side effects:
        - creates & populates new .md file for each tag (key) in dict
    """
    
    for tag, pages_list in tags_dict.items(): #i.e. for k,v in dict
        # .items() is required to iterate through dict containing list
        YAML_text = "---\ntitle: Tag:{}\n---\n\n## Articles\n\n".format(tag)
        tag_page  = "{}.md".format(tag)
        body_text = ""
        for page in pages_list:
            body_text += "-   [{0}](/{1})\n".format(page[0], page[1])
        tag_text = YAML_text + body_text
        save_file(target_directory, tag_page, tag_text)
        




# --- Higher order, main etc. ---

def main ():
    folders = ['../md', 'tags']
    tags_dict = {}
    
    make_folder(folders)
    for file in os.listdir('.'):
        if file.endswith(".md"):
            text = open_file(file)
            fixed_file = fix_filename(file)
            text = remove_H1(text)
            text = fix_intralinks(text)
            text = fix_wikilinks(text)
            text = create_sidenotes(text)
            update_tags_dict(tags_dict, fixed_file, text)
            save_file(folders[0], fixed_file, text)
    
    create_tag_pages(folders[1], tags_dict)         



    
if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()  
