import polib

def convert_po_to_mo(po_file_path, mo_file_path):
    # Load the .po file
    po = polib.pofile(po_file_path)

    # Save it as a .mo file
    po.save_as_mofile(mo_file_path)
    print(f"Conversion complete: {mo_file_path} created.")

# Example usage
po_file = r'MultiLingual\locales\hi\LC_MESSAGES\hi.po' # Replace with the actual .po file path
mo_file = r'MultiLingual\locales\hi\LC_MESSAGES\messages.mo'  # Replace with the desired output .mo file path

convert_po_to_mo(po_file, mo_file)

