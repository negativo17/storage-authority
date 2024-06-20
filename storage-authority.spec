%global debug_package %{nil}
#global __requires_exclude_from ^/opt/lsi/%{name}/bin/.*$
#global __provides_exclude_from ^/opt/lsi/%{name}/bin/.*$

# Docs at: https://techdocs.broadcom.com/us/en/storage-and-ethernet-connectivity/enterprise-storage-solutions/lsa-lsi-storage-authority-software/2-7.html

Name:           storage-authority
Version:        008.009.009.000
Release:        1%{?dist}
Summary:        Broadcom LSI Storage Authority
License:        Proprietary
URL:            https://www.broadcom.com/products/storage/raid-controllers
ExclusiveArch:  aarch64 x86_64

# Search at: https://www.broadcom.com/support/download-search?pg=Storage+Adapters,+Controllers,+and+ICs&pf=Storage+Adapters,+Controllers,+and+ICs&pn=&pa=&po=&dk=lsa&pl=&l=true
# Note that final URLs, tarball name and tarball structure keep on changing.
Source0:        https://docs.broadcom.com/docs-and-downloads/LSA_Linux_8_9-%{version}.zip
Source1:        https://docs.broadcom.com/docs-and-downloads/LSA_Linux_aarch64_8_9-%{version}.zip
Source2:        %{name}.service
Source3:        %{name}.xml

BuildRequires:  firewalld-filesystem
BuildRequires:  systemd-rpm-macros

Requires:       firewalld-filesystem
Requires(post): firewalld-filesystem
Requires:       openslp-server

# Compatibility names:
Provides:       LSA%{?_isa} == %{version}-%{release}
Provides:       LSIStorageAuthority%{?_isa} == %{version}-%{release}

%description
The LSI Storage Authority (LSA) is a web-based application that enables you to
monitor, maintain, troubleshoot, and configure the Broadcom MegaRAID products.

The LSI Storage Authority graphical user interface (GUI) helps you to view,
create, and manage storage configurations.

%prep
%ifarch x86_64
%autosetup -c
%if 0%{?rhel} == 8
mv LSA_Linux/gcc_8.3.x/LSIStorageAuthority-%{version}-00.x86_64.rpm .
%else
mv LSA_Linux/gcc_11.2.x/LSIStorageAuthority-%{version}-00.x86_64.rpm .
%endif
%endif

%ifarch aarch64
%autosetup -c -T -a 1
%if 0%{?rhel} == 8
mv LSA_Linux_aarch64/aarch64/LSIStorageAuthority-%{version}-00.aarch64.rpm .
%else
mv LSA_Linux_aarch64/aarch64/rhel9/LSIStorageAuthority-008.009.009.000-00.aarch64.rpm .
%endif
%endif

rpm2cpio *rpm | cpio -idm

# OpenPegasus and curl libraries, resolved automatically:
rm -frv opt/lsi/LSIStorageAuthority/bin/lib{curl,peg}*

# Default nginx SSL configuration
mv -fv opt/lsi/LSIStorageAuthority/server/conf/Sample_SSL_https/{nginx.conf,ssl.crt,ssl.key} \
    opt/lsi/LSIStorageAuthority/server/conf/

sed -i \
    -e 's/LSA_Default/9000/g' \
    -e 's/nginx_default/2463/g' \
    -e 's/protocol_type = 0/protocol_type = 1/g' \
    opt/lsi/LSIStorageAuthority/server/conf/nginx.conf \
    opt/lsi/LSIStorageAuthority/conf/LSA.conf

%build
# Nothing to build

%install
mkdir -p %{buildroot}/opt/lsi/%{name}
cp -fra opt/lsi/LSIStorageAuthority/{bin,conf,logs,plugins,report,server} %{buildroot}/opt/lsi/%{name}

install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
install -p -D -m 0644 %{SOURCE3} %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml

%post
%firewalld_reload
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%files
%license opt/lsi/LSIStorageAuthority/thirdparty/LSA-Licenses.txt
/opt/lsi/%{name}
%config /opt/lsi/%{name}/conf/LSA.conf
%config /opt/lsi/%{name}/server/conf/nginx.conf
%config /opt/lsi/%{name}/server/conf/ssl.key
%config /opt/lsi/%{name}/server/conf/ssl.crt
%{_prefix}/lib/firewalld/services/%{name}.xml
%{_unitdir}/%{name}.service

%changelog
* Thu Jun 20 2024 Simone Caronni <negativo17@gmail.com> - 008.009.009.000-1
- First build.
