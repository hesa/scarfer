def summarize_license(license_list):
    l_list = []
    for l in license_list:
        l_list.append(f'( {l} )')
    return " AND ".join(l_list)
        