from runners import *

if __name__ == '__main__':
    number = '27632528538'


    tdatas_base_path = r'C:\Users\gburgerfuck\Desktop\NOTPIXEL_RUNS\RUN_2710\data'
    tgportable_template_path = r'C:\Users\gburgerfuck\Desktop\TELEGRAMZ\tportable-template'
    keep_dir = r'C:\Users\gburgerfuck\Desktop\TELEGRAMZ'

    # run_tgportable(number, tdatas_base_path, tgportable_template_path, keep_dir)
    # registrate_tonkeeper(number, tdatas_base_path)
    #sb = SecFirefoxBrowser(proxy_host, proxy_port, proxy_user, proxy_password, wire=False)
    run_notpixels_browser(number, 'tdatas')
