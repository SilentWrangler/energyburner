import requests
import platform
import time
import webbrowser
import curses

def main(window):
    
    NAME = platform.node()
    REQUEST_AUTH_URL='https://the-tale.org/accounts/third-party/tokens/api/request-authorisation'
    headers = {'referer':'https://the-tale.org/'}
    payload = {'api_version':'1.0','api_client':'SWBURNER-0.1'}
    client = requests.session()
    resp = client.get('https://the-tale.org/accounts/third-party/tokens/api/authorisation-state',params=payload)
    csrf = client.cookies['csrftoken']
    data = resp.json()
    #print (resp.cookies)


    #print (data)
    if not data['data']['account_id']:
        payload1 = {'api_version':'1.0','api_client':'SWBURNER-0.1'}
        payload2 = {'application_name':"Silent Wrangler's Energy Burner",
                    'application_description':'Примитивный автосжигатель энегрии от игрока Sient Wrangler',
                    'application_info':NAME,
                    'csrfmiddlewaretoken':csrf}
        resp = client.post(REQUEST_AUTH_URL,params=payload1,data=payload2,headers=headers)
        d = resp.json()
        #print(d)
        window.addstr("Перейдите на страницу авторизации приложения\n")
        url = 'https://the-tale.org'+d['data']['authorisation_page']
        window.addstr(url)
        if platform=='android':
            import android
            android.Android().startActivity('android.intent.action.VIEW', url)
        webbrowser.open(url)
        window.addstr('\n\nКогда выдадите разрешение приложению, нажмите Enter')
        window.refresh()
        window.getch()

        
    payload = {'api_version':'1.0','api_client':'SWBURNER-0.1'}
    resp = client.get('https://the-tale.org/accounts/third-party/tokens/api/authorisation-state',params=payload)
    data = resp.json()
    
    #print(data)
    if data['data']['account_id']:
        info = client.get('https://the-tale.org/api/info',params=payload).json()
        
        try:
            helpcost = info['data']['abilities_cost']['help']
        except KeyError:
            window.addstr(str(info))
            window.getch()
            return
        
        window.nodelay(True)
        curses.noecho()
        while True:
            try:
                payload1 = {'api_version':'1.0','api_client':'SWBURNER-0.1'}
                payload2 = {'csrfmiddlewaretoken':csrf}
                resp = client.post('https://the-tale.org/game/abilities/help/api/use',params=payload1,data=payload2,headers=headers)
                d = resp.json()
                while d['status']=='processing':
                    time.sleep(1)
                    d = client.get('https://the-tale.org'+d["status_url"],params=payload1).json()
                energy = client.get('https://the-tale.org/game/api/info',params=payload1).json()['data']["account"]["energy"]
                window.clear()
                window.addstr("Нажмите Ctrl+C чтобы прервать процесс")
                window.addstr("\nОсталось энергии: {}".format(energy))
                window.refresh()
                number = window.getch()
                if number==3:
                    window.nodelay(False)
                    raise KeyboardInterrupt
                if energy<helpcost:
                    window.nodelay(False)
                    window.addstr("\nЭнергия кончилась! ")
                    window.refresh()
                    window.getch()
                    break
            except KeyboardInterrupt:
                window.addstr("\nПрервано")
                resp = client.post('https://the-tale.org/accounts/auth/api/logout',params=payload1,data=payload2,headers=headers)
                break
            
    else:
        window.nodelay(False)
        window.addstr("Разрешение ещё не выдано,  перезапустите и выдайте разрешение")
        window.refresh()
        window.getch()


curses.wrapper(main)
