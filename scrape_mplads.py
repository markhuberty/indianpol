import mechanize as m
import requests
import re
import unidecode
import time

form_url = 'http://mplads.nic.in/sslapps/mpladsworks/masterrep.ASP'
post_url = 'http://mplads.nic.in/sslapps/mpladsworks/Publicreports.ASP'

br = m.Browser()
br.addheaders = [('User-agent',
                  'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)')
                 ]

br.open(form_url)
br.select_form(nr=0)

# Start by looking by state
Hnames = br.form.find_control('Hname').items
hname_values = [item.name for item in Hnames]


form_dict = {}
for hvalue in ['R']:
    br['Hname'] = [hvalue]
    form_dict['Hname'] = hvalue
    br.submit()
    br.select_form(nr=0)
    state_items = br.form.find_control('State').items
    state_values = [item.name for item in state_items]
    state_labels = [item.attrs['label'] for item in state_items]
    for state, slabel in zip(state_values[1:], state_labels[1:]):
        br['State'] = [state]
        form_dict['State'] = state
        br.submit()
        br.select_form(nr=0)
        constituencies = br.form.find_control('ConstName').items
        const_values = [item.name for item in constituencies]
        const_labels = [item.attrs['label'] for item in constituencies]
        for constituency, clabel in zip(const_values[1:], const_labels[1:]):
            print slabel + ' '  + clabel
            br['ConstName'] = [constituency]
            form_dict['ConstName'] = constituency
            form_dict['Status'] = 'A'
            br.submit()
            br.select_form(nr=0)
            nodal_item = br.form.find_control('Nodal').value
            hnodal_item = br.form.find_control('HNodal').value
            form_dict['Nodal'] = nodal_item.strip()
            form_dict['HNodal'] = hnodal_item.strip()
            r = requests.post(post_url, data=form_dict)
            file_name = './data/' + hvalue + '_' + slabel + '_' + clabel + '_' + nodal_item.strip() + '.html'
            unicode_filename = unicode(file_name, errors='ignore')
            file_name = re.sub(' ', '_', unicode_filename)
            try:
                with open(file_name, 'wt') as f:
                    f.write(r.text.encode('UTF-8'))
            except:
                print 'Error writing ' + file_name
                continue
            time.sleep(2)
