from Test_Script.ts_multiple_display import display_function, generate_xml_file


def run():
    resolution_data = generate_xml_file.DisplaySetting('Portrait 2x2', {'DisplayPort-1': ['3840x2160', 60],
                                                                        'DisplayPort-2': ['3840x2160', 60],
                                                                        'DisplayPort-3': ['3840x2160', 60],
                                                                        'DisplayPort-4': ['3840x2160', 60]}).generate()
    display_function.check_resolution(resolution_data)


run()
