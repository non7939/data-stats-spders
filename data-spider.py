import requests
import json
import os
import time
import csv

class Tjg:
    def __init__(self):
        self.filename = "指标"
        self.url = 'http://data.stats.gov.cn/easyquery.htm'
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cookie': '_trs_uv=jteeg5x6_6_e8yq; JSESSIONID=D275F59AF5FC5F88EF129308372B610D; u=2; experience=show',
            'Referer': 'http://data.stats.gov.cn/easyquery.htm?cn=B01',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }

    def get_zb(self):
        data = {
            'id': 'zb',
            'dbcode': 'hgjd',
            'wdcode': 'zb',
            'm': 'getTree'
        }
        response = requests.post(self.url, headers = self.headers, data=data)
        dlists = json.loads(response.text)
        response.close()
        lists = []
        for x in dlists:
            hgjd = x['dbcode']
            id = x['id']
            zdname = x['name']
            zb = x['wdcode']
            #创建文件
            if not os.path.exists(self.filename):
                os.mkdir(self.filename)
            filename__zdname = os.path.join(self.filename,zdname)
            if not os.path.exists(filename__zdname):
                os.mkdir(filename__zdname)
            lists.append((hgjd, id, zdname,zb))  # hgjd A06 价格指数 zb
        return lists

    def get_title_id(self):
        for t in self.get_zb():
            hgjd, id, zdname, zb = t
            data = {
                'id': id,
                'dbcode': hgjd,
                'wdcode': zb,
                'm':'getTree'
            }
            response = requests.post(self.url, headers=self.headers, data=data)
            dlist = json.loads(response.text)
            response.close()
            for x in dlist:
                id = x['id']
                name = x['name']
                yield [id, name,zdname]

    def get_data(self, id, name,zdname):
        name = name.replace('(','').replace(")",'')
        kl = round(int(time.time() * 1000))
        params = {
            'm': 'QueryData',
            'dbcode': 'hgjd',
            'rowcode': 'zb',
            'colcode': 'sj',
            'wds': '[]',
            'dfwds': '[{"wdcode":"zb","valuecode":%s}]'%id,
            'k1': kl,
        }
        print(params)
        response = requests.get(self.url,headers=self.headers,params=params)
        # print(response.text)
        datas = json.loads(response.text)
        list_title = datas['returndata']['wdnodes'][0]['nodes']
        list_data = datas['returndata']['datanodes']
        lists = datas['returndata']['wdnodes'][1]['nodes']
        # quater_list = []#季度列表{'2018D': '2018年第四季度'}
        lcsv = [" "]
        for x in lists:
            sj = [x['code'], x['cname']]
            lcsv.append(sj[1])
        # print(lcsv)
        path_csv = os.path.join(self.filename,zdname,name) + '.csv'
        print(path_csv)
        if  not os.path.exists(path_csv):
            with open(path_csv,'a',encoding='gb18030',newline='')as f:
                winter = csv.writer(f)
                winter.writerow(lcsv)
        for x in list_title:
            # titles = []#标题列表{'A010101': '国内生产总值_当季值'}
            quater_list = [x['code'], x['cname']]
            l = [quater_list[1]]
            # print(quater_list)
            for y in list_data:
                # ['zb.A01012Q_sj.2014C': 88036.5]
                data_list =  [y['code'], y['data']['data']]
                # data = y['data']['data']
                if quater_list[0] in data_list[0]:
                    l.append(data_list[1])
            if os.path.exists(path_csv):
                with open(path_csv, 'a', encoding='gb18030', newline='')as f:
                    winter = csv.writer(f)
                    winter.writerow(l)
                print('下载完成：',l)

    def run(self):
        for i in self.get_title_id():
            id, name, zdname = i
            print(id, name, zdname)
            self.get_data(id,name,zdname)
            time.sleep(2)


if __name__ == "__main__":
    tjg = Tjg()
    tjg.run()