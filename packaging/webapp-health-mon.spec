Name:           webapp-health-mon
Version:        0.1
Release:        0
Summary:        A python script to monitor health of a web app
License:        GPLv2
URL:            https://github.com/weaselkeeper/misc_monitoring_scripts
Group:          System Environment/Base
Source0:        %{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-root-%(%{__id_u} -n)
BuildArch:      noarch

Requires:       python
Requires:       rpm-python
Requires:       python-argparse
Requires:       python-simplejson

%description
Monitor and alert based on specified criteria


%prep
%setup -q -n %{name}

%install
rm -rf %{buildroot}

%{__mkdir_p} %{buildroot}%{_bindir}
%{__mkdir_p} %{buildroot}%{_sysconfdir}/webapp-health-mon
%{__mkdir_p} %{buildroot}%{_localstatedir}/log/webapp-health-mon
cp -r ./*.py %{buildroot}%{_bindir}/
#cp -r ./*.conf %{buildroot}%{_sysconfdir}/webapp-health-mon

%files
%{_bindir}/*.py
#%{_sysconfdir}/webapp-health-mon/*
#%{_datadir}/webapp-health-mon/*

%pre

%post

%clean
rm -rf %{buildroot}

%changelog
* Sat Aug 02 2013 Jim Richardson <weaselkeeper@gmail.com> - 0.1
- Initial RPM build structure added.
