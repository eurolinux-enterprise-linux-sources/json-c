%global reldate 20130402
%global _libdir /%{_lib}
%define pkg_config_path %{_exec_prefix}/%{_lib}/pkgconfig

Name:		json-c
Version:	0.11
Release:	13%{?dist}
Summary:	A JSON implementation in C
Group:		Development/Libraries
License:	MIT
URL:		https://github.com/json-c/json-c/wiki
Source0:	https://github.com/json-c/json-c/archive/json-c-%{version}-%{reldate}.tar.gz

Patch0:		json-c-0.11-20130402-cve-2013-6370,6371.patch
Patch1:		json-c-0.11-20130402-strict-mode-nums.patch
Patch2:		json-c-0.11-20130402-strict-mode-quotes.patch
Patch3:		json-c-0.11-20130402-array-bounds-check.patch

%description
JSON-C implements a reference counting object model that allows you to easily
construct JSON objects in C, output them as JSON formatted strings and parse
JSON formatted strings back into the C representation of JSON objects.

%package devel
Summary:	Development headers and library for json-c
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	pkgconfig

%description devel
This package contains the development headers and library for json-c.

%package doc
Summary:	Reference manual for json-c
Group:		Documentation
BuildArch:	noarch

%description doc
This package contains the reference manual for json-c.

%prep
%setup -q -n json-c-json-c-%{version}-%{reldate}
%patch0 -p1 -b .cve-2013-6370,6371
%patch1 -p1 -b .strict-mode-nums
%patch2 -p1 -b .strict-mode-quotes
%patch3 -p1 -b .arr-bounds

for doc in ChangeLog; do
 iconv -f iso-8859-1 -t utf8 $doc > $doc.new &&
 touch -r $doc $doc.new &&
 mv $doc.new $doc
done

%build
%configure \
  --disable-static \
  --enable-rdrand \
  --enable-shared \

# get rid of rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

# parallel build is broken for now, make %{?_smp_mflags}
make V=1

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

# Get rid of la files
rm -rf %{buildroot}%{_libdir}/*.la

# yum cannot replace a dir by a link
# so switch the dir names
rm %{buildroot}%{_includedir}/json
mv %{buildroot}%{_includedir}/json-c \
   %{buildroot}%{_includedir}/json
ln -s json \
   %{buildroot}%{_includedir}/json-c

# 'make install' places *.pc files in %%{_libdir} which
# does not have %%{_exec_prefix} in json-c's case, so we
# have to move the pkg-config directory to its right place.
mkdir -p %{buildroot}%{pkg_config_path}
mv -T %{buildroot}%{_libdir}/pkgconfig/ \
   %{buildroot}%{pkg_config_path}

# temporarily disabled
#%%check
#make check

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING README README.html
%{_libdir}/libjson.so.*
%{_libdir}/libjson-c.so.*

%files devel
%defattr(-,root,root,-)
%{_includedir}/json
%{_includedir}/json-c
%{_libdir}/libjson.so
%{_libdir}/libjson-c.so
%{pkg_config_path}/json.pc
%{pkg_config_path}/json-c.pc

%files doc
%defattr(-,root,root,-)
%doc doc/html/*

%changelog
* Fri Oct 21 2016 Radovan Sroka <rsroka@redhat.com> 0.11.13
- enable debuginfo package
  resolves: rhbz#1382707

* Mon Mar 02 2015 Jakub Filak <jfilak@redhat.com> - 0.11-12
- place pkg-config *.pc files in the correct directory
  resolves: #1158842

* Tue Aug 26 2014 Petr Lautrbach <plautrba@redhat.com> 0.11-11
- move libraries from /usr/lib* to /lib*
  resolves: #1134001

* Mon Jun 16 2014 Tomas Heinrich <theinric@redhat.com> - 0.11-10
- add a patch to do proper array bounds check
  resolves: #966964

* Wed May 21 2014 Tomas Heinrich <theinric@redhat.com> - 0.11-9
- initial import
  - disable building of a debuginfo package - works around rhbz 903009
  - add a workaround for disabling rpath
  - disable paralel build
  - disable 'check' section for now
  resolves: #966964
