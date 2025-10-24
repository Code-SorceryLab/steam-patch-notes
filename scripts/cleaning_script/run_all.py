import filter_patch_notes
import strip_html

def main(raw_news_path, output_filtered_path, output_html_cleaned_path):
    filter_patch_notes.main(raw_news_path,output_filtered_path)
    strip_html.main(output_filtered_path, output_html_cleaned_path)

if __name__ == "__main__":
    '''
    Add the paths to the raw news data, filtered output, 
    and HTML cleaned output here respectively.
    '''
    main("...", "...", "...")