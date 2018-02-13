import csv
from ..Tag import TagFactory
import warnings
from datetime import timedelta
import re

# TODO: Replace Offset with Guntime
class Registration():
    class Registrant():
        def __init__(self, reg, bib, tag_id, first, last, sex,
                     division, offset_minutes, hs, univ, ag,
                     timeadjust, relay_name):
            def isname(s):
                return re.fullmatch('[a-zA-Z-\s]*', s) != None
                
            if(not(isinstance(bib, str) and bib.isdigit())):
                raise ValueError('Bib must be number. E.g. \'42\'')
            self.__bib = bib

            self.__tag = TagFactory.register_tag(tag_id)

            if(not isinstance(first, str)):
                raise ValueError('First name must be a string. E.g. \'John\'')
            elif(not isname(first)):
                warnings.warn(f'Possible malformed first name: {first}',
                              category=self.MalformedWarning)
            elif(not isinstance(last, str)):
                raise ValueError('Last name must be a string. E.g. \'Doe\'')
            elif(not isname(last)):
                warnings.warn(f'Possible malformed last name: {last}',
                              category=self.MalformedWarning)

            self.__name = (first, last)

            if(division not in reg.divisions):
                raise ValueError(f'Invalid Division entry: {division}. '\
                                 f'Valid entries are '\
                                 f'{reg.divisions}')

            self.__division = division
            
            if division == 'High School':
                if(not isinstance(univ, str)):
                    raise ValueError(f'High School Division participant '\
                                     f'\'{first} {last}\' '\
                                     f'has invalid High School name. Got: '
                                     f'\'{hs}\'')
                elif(hs == ''):
                    raise ValueError(f'High School Division participant '\
                                     f'\'{first} {last}\' '\
                                     f'missing High School name. Got:{hs}')
                elif(not(isname(hs))):
                    warnings.warn(f'Malformed High School name: {hs}',
                                  category=self.MalformedWarning)
                self.__hs = hs
            else:
                self.__hs = None

            if division == 'Collegiate':
                if(not isinstance(univ, str)):
                    raise ValueError(f'Collegiate Division participant '\
                                     f'\'{first} {last}\' '\
                                     f'has invalid university name. Got:{univ}')
                elif(univ == ''):
                    raise ValueError(f'Collegiate Division participant '\
                                     f'\'{first} {last}\' '\
                                     f'missing University name. Got:{univ}')
                elif(not(isname(univ))):
                    warnings.warn(f'Malformed University name: {univ}',
                                  category=self.MalformedWarning)
                self.__univ = univ
            else:
                self.__univ = None

            if division == 'Relay':
                if(not isinstance(relay_name, str)):
                    raise ValueError(f'Relay Division participant '\
                                     f'\'{first} {last}\' '\
                                     f'has invalid team name. Got:{relay_name}')
                elif(relay_name == ''):
                    raise ValueError(f'Relay Division participant '\
                                     f'\'{first} {last}\' '\
                                     f'missing team name. Got:{relay_name}')
                elif(not(isname(relay_name))):
                    warnings.warn(f'Malformed team name: {relay_name}',
                                  category=self.MalformedWarning)
                self.__relay_name = relay_name
            else:
                self.__relay_name = None

            if(sex not in reg.sexes):
                raise ValueError(f'Invalid Sex entry: {sex}. '
                                 f'Valid entries are '
                                 f'{self.__SEX_VALUES}')

            self.__sex = sex

            if(ag not in reg.age_groups):
                raise ValueError(f'Invalid Age Group entry: {ag}. '
                                 f'Valid entries are '
                                 f'{reg.age_groups}')

            self.__ag = ag

            if(not isinstance(timeadjust, str)):
                raise ValueError(f'Time Adjustment for participant '\
                                 f'\'{first} {last}\' '\
                                 f'invalid. Got:{timeadjust}')
            elif(timeadjust != ''):
                warnings.warn(f'Field Time Adjustment not empty for '
                              f'registarant {first} {last}. This '
                              f'feature is not implemented')

            try:
                off = (int(offset_minutes))
            except ValueError:
                raise ValueError(f'Time Offset must be number. E.g. \'42\' '
                                 f'Got \'{offset_minutes}\'')
            self.__offset = timedelta(minutes=off)

            if division == 'Paratriathlete' and off != timedelta(minutes=0):
                warnings.warn(f'{self.name[0]} {self.name[1]} with division '
                              f'\'Paratriathlete\' '
                              f'Has non-zero timing offset. Shouldn\'t they be '
                              f'in wave 1, with field \'Offset (min)\' of 0?',
                              category=self.RegistrationWarning)

        @property
        def division(self):
            return self.__division 

        @property
        def tag(self):
            return self.__tag 

        @property
        def name(self):
            return self.__name

        @property
        def sex(self):
            return self.__sex

        @property
        def division(self):
            return self.__division

        @property
        def offset(self):
            return self.__offset

        @property
        def hs(self):
            if(self.division != "High School"):
                raise ValueError(f'Registrant {self.name[0]} '
                                 f'{self.name[1]} is in Division '
                                 f'{self.division}, but High School'
                                 f'field was queried')
            return self.__hs

        @property
        def university(self):
            if(self.division != "Collegiate"):
                raise ValueError(f'Registrant {self.name[0]} '
                                 f'{self.name[1]} is in Division '
                                 f'{self.division}, but University'
                                 f'field was queried')
            return self.__univ

        @property
        def age_group(self):
            div = self.division
            if(div != "Elite" or div != "Open"):
                raise ValueError(f'Registrant {self.name[0]} '
                                 f'{self.name[1]} is in Division '
                                 f'{self.division}, but University'
                                 f'field was queried')
            return self.__univ

        @property
        def age_group(self):
            return self.__ag

        class MalformedWarning(Warning):
            def __init__(self,*args,**kwargs):
                Warning.__init__(self,*args,**kwargs)

        class RegistrationWarning(Warning):
            def __init__(self,*args,**kwargs):
                Warning.__init__(self,*args,**kwargs)

    __HEADER_FIELDS = ['Bib #', 'RFID', 'First Name', 'Last Name',
                       'Sex', 'Division', 'Offset (min)',
                       'High School', 'University',
                       'Age Group', 'Time Adjustment', 'Relay Name']
    __AGE_GROUP_RANGE = (20, 70)
    __AGE_GROUP_PERIODS = {1, 5, 10}
    __DIVISION_VALUES = {'Collegiate', 'High School', 'Elite', 'Relay', 'Open', 'Paratriathlete'}
    __SEX_VALUES = {'Male', 'Female'}

    # TODO: Double and triple check these fields
    @property 
    def age_groups(self):
        return self.__ag_values

    @property 
    def divisions(self):
        return self.__DIVISION_VALUES

    @property 
    def sexes(self):
        return self.__SEX_VALUES

    def __gen_ag_values(self, agp):
        min = self.__AGE_GROUP_RANGE[0]
        max = self.__AGE_GROUP_RANGE[1]
        vals = {f'U{min}', f'{max}+'}
        for low in range(min, max, agp):
            high = low + agp - 1
            vals.add(f'{low}-{high}')
        return vals

    def __init__(self, name, agperiod):
        if(not (isinstance(name, str))):
            raise RuntimeError('Argument name (Reader Name) must '
                               'be a string')
        self.__name = name

        if(agperiod not in self.__AGE_GROUP_PERIODS):
            raise ValueError(f'Invalid Age Group Period {agperiod}.'
                             f'Valid values are: {self.__AGE_GROUP_PERIODS}')

        self.__ag_values = self.__gen_ag_values(agperiod)

        self.__reg = self.__parse_csv(name)

    def __getitem__(self, tag):
        return self.__reg[tag]
        
    def __parse_csv(self, name):
        registration = dict()
        with open(f'{name}.csv', newline='') as csvf:
            sample = csvf.read()
            csvf.seek(0)

            self.sniffer = csv.Sniffer()
            dialect = self.sniffer.sniff(sample)
            rdr = csv.reader(csvf, dialect)

            has_header = self.sniffer.has_header(sample)
            if not has_header:
                raise ValueError('Malformed .csv File: No header found!')

            header = rdr.__next__()
            fieldmap = dict()
            for field in self.__HEADER_FIELDS:
                try:
                    fieldmap[field] = header.index(field)
                except ValueError:
                    raise ValueError(f'Malformed .csv File: Column \'{field}\' not found!')

            reg = [{field : line[fieldmap[field]]
                    for field in self.__HEADER_FIELDS}
                   for line in rdr]

            for entry in reg:
                bib = entry['Bib #'].strip()
                tag_id = entry['RFID'].strip()
                first = entry['First Name'].strip()
                last = entry['Last Name'].strip()
                sex = entry['Sex'].strip()
                division = entry['Division'].strip()
                offset_minutes = entry['Offset (min)'].strip()
                highschool = entry['High School'].strip()
                univ = entry['University'].strip()
                ag = entry['Age Group'].strip()
                timeadjust = entry['Time Adjustment'].strip()
                relay_name = entry['Relay Name'].strip()
                registrant = self.Registrant(self, bib, tag_id, first, last, sex,
                                        division, offset_minutes,
                                        highschool, univ, ag,
                                        timeadjust, relay_name)
                
                registration[registrant.tag] = registrant
        return registration

    def __iter__(self):
        for k,v in self.__reg.items():
            yield v

    def __registrant_selftest(self):
        # TODO: Write Tests!
        pass

