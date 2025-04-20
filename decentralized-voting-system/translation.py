import polib
from googletrans import Translator

# Load  original .pot file
po = polib.pofile(r"C:\Users\prade\ByteBug-Project\decentralized-voting-system\backend\messages.pot")  
translator = Translator()


for entry in po:
    if not entry.msgstr.strip() and entry.msgid.strip():
        try:
            translated = translator.translate(entry.msgid, src='en', dest='hi')
            entry.msgstr = translated.text  # Set translated text to msgstr
            print(f'Translated: {entry.msgid} --> {entry.msgstr}')
        except Exception as e:
            print(f"Error translating '{entry.msgid}': {e}")

# Save .po file
po.save(r"C:\Users\prade\ByteBug-Project\decentralized-voting-system\backend\MultiLingual\locales\hi\LC_MESSAGES\hi.po") 
print("\n✅ Translated .po saved as 'hi.po'")
