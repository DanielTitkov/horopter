import re


class TextCleaner:
    def __init__(self, clean_params):
        self.common_rgxp = '[\n\t\r]'
        self.common = clean_params.get('common', 1)
        self.delete = clean_params.get('delete', [])
        self.replace = clean_params.get('replace', [])
        
    
    def deleting(self, string):
        for item in self.delete:
            string = self.cleanse(item, string)
        return string
    
    
    def replacing(self, string):
        """Not yet supported due to lack of practical need"""
        return string
    
    
    def complete_task(self, string):
        if self.common:
            string = self.cleanse(self.common_rgxp, string)
        string = self.deleting(string)
        string = self.replacing(string)
        return string.strip()
    
    
    @staticmethod
    def cleanse(rgxp, string):
        emoji_rgxp = '[^\w\s!?@#$%^&*\(\)\{\}\[\],.:;-_]' # to avoid utf8mb for MySQL
        return re.sub(' +', ' ', re.sub(emoji_rgxp, ' ', re.sub(rgxp, ' ', string)))