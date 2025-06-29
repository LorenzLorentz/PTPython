from NECCrawler import NECCrawler
from MusicCrawler import MusicCrawler
from tqdm import tqdm

def get_song_task(crawler:MusicCrawler, song_id:str):
    crawler.get_song_info(song_id=song_id).save()

def get_singer_task(crawler:MusicCrawler, singer_id:str):
    crawler.get_singer_info(singer_id=singer_id).save()

def task(cookie:str=r"_ntes_nnid=43d0a9152eefd1d52744655562e55797,1729407544382; _ntes_nuid=43d0a9152eefd1d52744655562e55797; WNMCID=dwsxzy.1729407545166.01.0; __snaker__id=waoxQcF2fxDIxtot; P_INFO=19112012800|1751007075|1|music|00&99|null&null&null#chq&null#10#0|&0|null|19112012800; MUSIC_U=00F77E6B2F87AC934FFD485275369FC8F5F7C8B23DB92408E00E2FD7C66931020C14D91A406F5FD2C3B592D0435C40EFF6D45E7C049FC4DCB25800EF70444062B3C8848F71CB6C3D7749AA83170023A5E961AD010FDD9BED6BC74278BB87A6798F31CFE291B6B6A93FBB392C838ED5CD463606C793829B0BE2AD6CD8B0280BCD615FE13B47D7A679E6FCC2A3CE0D531F85D0C22A9D533AC5AFFAB4B23F32B6F39A9E91493AC9A528E189D1CBF02887831611F8C05B65EF0B359068A427085B1B5B46C074D63E6CC4E5C6DC928959D58B456FA4D8D97267BFFC58D8A2D238AE8DE43E18494CADF15D2B220845927DFBC8847E0C223BE1988E5724A4FAAE0B03145B5239B4F31F7190989B761439A4042728607EED474D2F7166965884996C5B3A9BEB487D0E4FFD25EF2068B0BFC9991E34089A648A41BD49D6667D1F01D5E6F8AE3BDE4093E0A4D38517E39DA5CCDF30F9; __csrf=1db06a312a7d023e241d12a38384910c; __remember_me=true; gdxidpyhxdE=fnECaVxCS%5C2HzVbep3%2FIpWrSY3sinqaADYDzlbQWExjpN%5Cxs5iICiThvs9lmSaae4O%2FIQUb28MLrQI4VjoDYv061Z86u7Ldtr%2Bba68cqkJsLNEzxsaXUmmudfDSuCD97ECWeBwYjBJcmxb7K3gKz3NSSjntcAPEBubzq7tjA%2B3CKsrog%3A1751008628286; NMTID=00OSWVVYQnY-eNUGUjKhZEk__jepoMAAAGXsdnhHA; WEVNSM=1.0.0; WM_TID=h6qpg4uzMpNERURBEQaHTdnV2oMAlEfc; WM_NI=UAjEQ%2B7jSmZHPsmgii2DVYHo%2FrPZroxxaTFeczYSrDYHwL1KMb5%2BAlRSZP9I%2FoKs69FGAN5%2F8Qb5G0ET3TKPm%2B6ofepZOZWK7%2FtoHICUoWCYb%2B2xTlCZsVwMmYcN4qj9aDk%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee8daa3fb49d8ad0cc5991ef8ba2c15f839a8badd76badebb7b3d86aafaca8d7b62af0fea7c3b92a979fa6a6d421f5b69d8ed94494ada388ec63f29c9abacb65edaea0bbf165bca8afb5c56fa1a697b4f1509b98b9adb4418fbefbccc468928d96b1bc43edb18594b53386998fafb825fc8faed6c63c878cfdb5ca5caff5fa90e56fb48681bbd641f5f1bc90cb43818ba1b8c253a2f5fe99d7688186bdb7f647af87adafb77baae7afa5ea37e2a3; _iuqxldmzr_=32; playerid=71245658; JSESSIONID-WYYY=vO85zh6xjFz3q%2B7JAY5AeVlC3GtTH2IYm42vTybf6cB9jAiqaVeyOMj7g%2Fwxtwir7zKu1hdxVGBMZr6CjoRxtO4oRKaCAYf3bD7ZJBm5NeyBZAxCRjfH3gTSIRoNZbzTaEPCatan0dvik2UU%2Bevci5pvqEHhad3dq1zw7RUTk7G5u8%5Ci%3A1751131284154"):
    crawler = NECCrawler(cookie=cookie)

    # """
    num_fail_song = 0
    with tqdm(range(180000, 190000), desc="Processing Songs") as pbar:
        for song_id in pbar:
            try:
                get_song_task(crawler=crawler, song_id=str(song_id))
            except Exception as e:
                num_fail_song += 1
            pbar.set_postfix(fails=num_fail_song)
    # """
    
    """
    num_fail_singer = 0
    with tqdm(range(5000, 9000), desc="Processing Singers") as pbar:
        for singer_id in pbar:
            try:
                get_singer_task(crawler=crawler, singer_id=str(singer_id))
            except Exception as e:
                num_fail_singer += 1
            pbar.set_postfix(fails=num_fail_singer)
    """

if __name__ == "__main__":
    task()