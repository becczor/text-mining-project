# xml-to-text
# Author: Rebecca Lindblom
import re

def xml_to_text(input_file, output_file):

	start = '<sentence'
	end = '</sentence>'
	numbers = []
	rf = open(input_file, 'r', encoding="utf-8")
	wf = open(output_file, "a", encoding="utf-8")
	print("both files opened")
	started = False
	# Read one line at a time
	for line in rf:
		# If there is an end in the line, the collected sentence should be processed.
		if end in line:
			started = False
			# Find all raw words in sentence and add to a list
			sentence_words = [re.findall(r'>.+<', content) for content in sentence]
			sentence_words = [' '.join([word[1:-1] for word in words]) for words in sentence_words]

			processed = ' '.join(sentence_words)
			#processed = clean_sentence(' '.join(sentence_words))
			try:
				wf.write(processed + '\n')
			except Exception as e:
				print("Error: ", e)
				print(processed)
				raise e
		# If we have started, the line should be appended to sentence. 
		if started:
			sentence.append(line)
		# Reset sentence list and start over.
		if start in line:
			started = True
			sentence = []

	rf.close()
	wf.close()
	print("both files closed")



# Files to read:
# flashback-livsstil.xml
# familjeliv-allmanna-noje.xml
# familjeliv-svartattfabarn.xml
# flashback-mat.xml
# flashback-ovrigt.xml
# https://spraakbanken.gu.se/swe/resurs/familjeliv-allmanna-kropp
# https://spraakbanken.gu.se/swe/resurs/familjeliv-allmanna-hushem
xml_to_text("flashback-ovrigt.xml", "sentences.txt")