import mechanize as m
import requests
import re
import unidecode
import time

form_url = 'http://mplads.nic.in/sslapps/mpladsworks/masterrep.ASP'
post_url = 'http://mplads.nic.in/sslapps/mpladsworks/Publicreports.ASP'

# Instantiate a browser, fake it as IE
br = m.Browser()
br.addheaders = [('User-agent',
                  'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)')
                 ]

br.open(form_url)
br.select_form(nr=0)

# Start by looking by House
Hnames = br.form.find_control('Hname').items
hname_values = [item.name for item in Hnames]


form_dict = {}
for hvalue in ['L']: # 'L' doesn't work right now
    br['Hname'] = [hvalue]
    form_dict['Hname'] = hvalue
    br.submit()
    br.select_form(nr=0)

    # Get the states that have MPs in this house
    state_items = br.form.find_control('State').items
    state_values = [item.name for item in state_items]
    state_labels = [item.attrs['label'] for item in state_items]

    # Note the [1:]; the lists all have dummy values in the 0th position, skip those
    for state, slabel in zip(state_values[1:], state_labels[1:]):
        br['State'] = [state]
        form_dict['State'] = state

        try:
            br.submit()
        except m.ItemNotFoundError:
            continue
        br.select_form(nr=0)

        ## Get the constituencies for this state.
        constituencies = br.form.find_control('ConstName').items
        const_values = [item.name for item in constituencies]
        const_labels = [item.attrs['label'] for item in constituencies]
        
        for constituency, clabel in zip(const_values[1:], const_labels[1:]):
            print slabel + ' '  + clabel
            br['ConstName'] = [constituency]
            form_dict['ConstName'] = constituency

            
            #'A' is for all 
            form_dict['Status'] = 'A'

            try:
                br.submit()
            except m.ItemNotFoundError:
                continue
            br.select_form(nr=0)

            # Must populate this stuff for R, not sure about L
            nodal_item = br.form.find_control('Nodal').value
            form_dict['Nodal'] = nodal_item.strip()
            try:
                hnodal_item = br.form.find_control('HNodal').value
            except:
                hnodal_item = ''
            form_dict['HNodal'] = hnodal_item.strip()

            if hvalue == 'L':
                hno_items = br.form.find_control('Hno').items
                hno_values = [item.name for item in hno_items]
                for hno in hno_values[1:]:
                    br['Hno'] = [str(hno)]
                    form_dict['Hno'] = str(hno)
                    try:
                        br.submit()
                    except m.ItemNotFoundError:
                        continue
                    br.select_form(nr=0)

                    form_dict['name'] = br.form.find_control('name').value
                    form_dict['Hidname'] = br.form.find_control('Hidname').value
                    
            # Issue the POST request
            r = requests.post(post_url, data=form_dict)

            # Write out the HTML as utf-8. If it fails, too bad.
            file_name = hvalue + '_' + slabel + '_' + clabel + '_' + nodal_item.strip() + '.html'
            unicode_filename = unicode(file_name, errors='ignore')
            file_name = re.sub(' ', '_', unicode_filename)

            if hvalue == 'L':
                file_name = './data/' + re.sub(' ', '_', form_dict['name']) + '_' + file_name
            else:
                file_name = './data/' + file_name
                
            try:
                with open(file_name, 'wt') as f:
                    f.write(r.text.encode('UTF-8'))
            except:
                print 'Error writing ' + file_name
                continue
            
            # Don't overload the poor website...
            time.sleep(2)
