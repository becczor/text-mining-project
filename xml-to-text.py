# xml-to-text

import re

punctuation = [',', '-', "'", '*', '_', '.']

def clean_sentence(text):
	if text[-1] in punctuation:
		text = text[:-1]

	return text.lower()




def xml_to_text(filename):

	f = open(filename, 'r', encoding="utf-8")
	text = '\n'.join(f.readlines())


	#print(text[4350760:4350770])
	sentences_tags = re.findall(r'<sentence(?:(?!sentence>)[\s\S])*', text)

	# Find all words, which can be found between
	sentence_words = [re.findall(r'>.+<', content) for content in sentences_tags]
	sentence_words = [' '.join([word[1:-1] for word in words]) for words in sentence_words]


	#print(sentence_words[0:10])
	w = open("sentences.txt", "a", encoding="utf-8")
	print("file opened")

	for sentence in sentence_words:
		processed = clean_sentence(sentence)
		try:
			w.write(processed + '\n')
		except Exception as e:
			print("Error: ", e)
			print(processed)
			raise e
		
		

	print("file written")
	w.close()
	print("file closed")
	

	



xml_to_text("familjeliv-pappagrupp_2.xml")

