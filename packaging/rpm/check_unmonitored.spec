Name:           check_unmonitored
Version:        0.1
Release:        1
Summary:        Alert if machines are left too long in unmonitored state.
License:        GPLv2
URL:            https://github.com/weaselkeeper/misc_monitoring_scripts
Group:          System Environment/Base
Source0:        %{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-root-%(%{__id_u} -n)
BuildArch:      noarch

Requires:       python

%description
Alert if machines are left too long in unmonitored state

%prep
%setup -q -n %{name}

%install
rm -rf %{buildroot}

%{__mkdir_p} %{buildroot}%{_bindir}
%{__mkdir_p} %{buildroot}%{_sysconfdir}/%{name}
%{__mkdir_p} %{buildroot}%{_localstatedir}/log/%{name}
cp -r ./*.py %{buildroot}%{_bindir}/
cp -r ./*.conf %{buildroot}%{_sysconfdir}/%{name}

%files
%{_bindir}/*.py
%{_sysconfdir}/%{name}/*.conf

%pre

%post

%clean
rm -rf %{buildroot}

%changelog
* Wed Aug 28 2013 Jim Richardson <weaselkeeper@gmail.com> - 0.1-1
- add debug flag
* Thu Aug 15 2013 Jim Richardson <weaselkeeper@gmail.com> - 0.1
- Initial RPM build structure added.
