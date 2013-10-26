Name:           misc_monitoring
Version:        %(git describe | sed -e 's/-/_/g')
Release:        0
Summary:        Alert if machines are left too long in unmonitored state.
License:        GPLv2
URL:            https://github.com/weaselkeeper/misc_monitoring_scripts
Group:          System Environment/Base
Source0:        %{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-root-%(%{__id_u} -n)
BuildArch:      noarch


%description
Small monitoring scripts for misc tasks.

# Sub packages

%package  check_unmonitored
Summary:	Check zabbix for hosts in umonitored state
Requires:	python
BuildArch:      noarch

%description check_unmonitored
Check zabbix for hosts in umonitored state 

%package webapp_health_mon
Summary:	Monitors a web app via url gets with json results.
Requires:	python
BuildArch:	noarch

%description webapp_health_mon
Monitors a web app via url gets with json results.

%package svncheck
Summary:	Monitors an svn sync system we no longer use
Requires:	python
BuildArch:	noarch

%description svncheck
Monitors an svn sync system we no longer use.
Left here for posterity.

%prep
%setup -q -n %{name}

%install
rm -rf %{buildroot}


%{__mkdir_p} %{buildroot}%{_bindir}
%{__mkdir_p} %{buildroot}%{_sysconfdir}/%{name}
%{__mkdir_p} %{buildroot}%{_localstatedir}/log/%{name}
cp -r ./*.py %{buildroot}%{_bindir}/
cp -r ./*.conf %{buildroot}%{_sysconfdir}/%{name}

%files check_unmonitored
%{_bindir}/check_unmonitored.py
#%{_sysconfdir}/%{name}/*.conf

%files webapp_health_mon
%{_bindir}/webapp-monitor.py
#%{_bindir}/*.py[co]
%{_sysconfdir}/%{name}/*.conf

%files svncheck
%{_bindir}/svncheck.py

%pre

%post

%clean
rm -rf %{buildroot}

%changelog
* Wed Aug 28 2013 Jim Richardson <weaselkeeper@gmail.com> - 0.1-1
- add debug flag
* Thu Aug 15 2013 Jim Richardson <weaselkeeper@gmail.com> - 0.1
- Initial RPM build structure added.
