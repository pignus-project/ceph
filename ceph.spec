Name:          ceph
Version:       0.53
Release:       1%{?dist}
Summary:       User space components of the Ceph file system
License:       LGPLv2
Group:         System Environment/Base
URL:           http://ceph.com/

Source:        http://ceph.com/download/%{name}-%{version}.tar.bz2
Patch0:        ceph-init-fix.patch
Patch1:        ceph.logrotate.patch
Patch2:        ceph-build-support-for-automake-1.12.patch

BuildRequires: fuse-devel, libtool, libtool-ltdl-devel, boost-devel, 
BuildRequires: libedit-devel, fuse-devel, git, perl, gdbm, libaio-devel,
# google-perftools is not available on these:
%ifnarch ppc ppc64 s390 s390x
BuildRequires: gperftools-devel
%endif
BuildRequires: cryptopp-devel, libatomic_ops-devel, gcc-c++
BuildRequires: pkgconfig, libcurl-devel, keyutils-libs-devel
BuildRequires: gtkmm24-devel, gtk2-devel, libuuid, libuuid-devel
BuildRequires: leveldb-devel, snappy-devel

Requires(post): chkconfig, binutils, libedit
Requires(preun): chkconfig
Requires(preun): initscripts

%description
Ceph is a distributed network file system designed to provide excellent
performance, reliability, and scalability.

%package libs
Summary:       Ceph libraries
Group:         System Environment/Libraries
%description libs
Common libraries for Ceph distributed network file system

%package libcephfs
Summary:       Ceph libcephfs libraries
Group:         System Environment/Libraries
%description libcephfs
libcephfs library for Ceph distributed network file system

%package       fuse
Summary:       Ceph fuse-based client
Group:         System Environment/Base
Requires:      %{name} = %{version}-%{release}
BuildRequires: fuse-devel
%description   fuse
FUSE based client for Ceph distributed network file system

%package     devel
Summary:     Ceph headers
Group:       Development/Libraries
License:     LGPLv2
Requires:    %{name} = %{version}-%{release}
Requires:    %{name}-libs = %{version}-%{release}
Requires:    %{name}-libcephfs = %{version}-%{release}
%description devel
This package contains the headers needed to develop programs that use Ceph.

%package radosgw
Summary:        rados REST gateway
Group:          Development/Libraries
Requires:       mod_fcgid
BuildRequires:  fcgi-devel
BuildRequires:  expat-devel

%description radosgw
radosgw is an S3 HTTP REST gateway for the RADOS object store. It is
implemented as a FastCGI module using libfcgi, and can be used in
conjunction with any FastCGI capable web server.

%prep
%setup -q
%patch0 -p1 -b .init
%patch1 -p0
%patch2 -p1

%build
./autogen.sh

%ifarch armv5tel
# libatomic_ops does not have correct asm for ARMv5tel
EXTRA_CFLAGS="-DAO_USE_PTHREAD_DEFS"
%endif
%ifarch %{arm}
# libatomic_ops seems to fallback on some pthread implementation on ARM
EXTRA_LDFLAGS="-lpthread"
%endif

%{configure} --prefix=/usr --sbindir=/sbin \
--localstatedir=/var --sysconfdir=/etc \
%ifarch ppc ppc64 s390 s390x
--without-tcmalloc \
%endif
--with-system-leveldb --without-hadoop --with-radosgw --with-gtk2 \
CFLAGS="$RPM_OPT_FLAGS $EXTRA_CFLAGS" \
CXXFLAGS="$RPM_OPT_FLAGS $EXTRA_CFLAGS -fvisibility-inlines-hidden" \
LDFLAGS="$EXTRA_LDFLAGS"

make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -type f -name "*.la" -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type f -name "*.a" -exec rm -f {} ';'
install -D src/init-ceph $RPM_BUILD_ROOT%{_initrddir}/ceph
chmod 0644 $RPM_BUILD_ROOT%{_docdir}/ceph/sample.ceph.conf
install -m 0644 -D src/logrotate.conf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/ceph
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/ceph/tmp/
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/ceph/
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/ceph/stat
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/ceph
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d

%post
/sbin/chkconfig --add ceph

%preun
if [ $1 = 0 ] ; then
    /sbin/service ceph stop >/dev/null 2>&1
    /sbin/chkconfig --del ceph
fi

%postun
if [ "$1" -ge "1" ] ; then
    /sbin/service ceph condrestart >/dev/null 2>&1 || :
fi

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig
%post libcephfs -p /sbin/ldconfig
%postun libcephfs -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc README COPYING
%dir %{_sysconfdir}/ceph
%{_bindir}/ceph
%{_bindir}/cephfs
%{_bindir}/ceph-conf
%{_bindir}/ceph-clsinfo
%{_bindir}/crushtool
%{_bindir}/monmaptool
%{_bindir}/osdmaptool
%{_bindir}/ceph-authtool
%{_bindir}/ceph-syn
%{_bindir}/ceph-run
%{_bindir}/ceph-mon
%{_bindir}/ceph-mds
%{_bindir}/ceph-osd
%{_bindir}/ceph-rbdnamer
%{_bindir}/librados-config
%{_bindir}/rados
%{_bindir}/rbd
%{_bindir}/ceph-debugpack
%{_bindir}/ceph-coverage
%{_bindir}/ceph-dencoder
%{_initrddir}/ceph
/sbin/mkcephfs
/sbin/mount.ceph
/sbin/ceph-disk-activate
/sbin/ceph-disk-prepare
/sbin/ceph-create-keys
%{_libdir}/ceph
%{_docdir}/ceph/sample.ceph.conf
%{_docdir}/ceph/sample.fetch_config
%config(noreplace) %{_sysconfdir}/logrotate.d/ceph
%config(noreplace) %{_sysconfdir}/bash_completion.d/rados
%config(noreplace) %{_sysconfdir}/bash_completion.d/ceph
%config(noreplace) %{_sysconfdir}/bash_completion.d/rbd
%{_mandir}/man8/ceph-mon.8*
%{_mandir}/man8/ceph-mds.8*
%{_mandir}/man8/ceph-osd.8*
%{_mandir}/man8/mkcephfs.8*
%{_mandir}/man8/ceph-run.8*
%{_mandir}/man8/ceph-syn.8*
%{_mandir}/man8/crushtool.8*
%{_mandir}/man8/osdmaptool.8*
%{_mandir}/man8/monmaptool.8*
%{_mandir}/man8/ceph-conf.8*
%{_mandir}/man8/ceph.8*
%{_mandir}/man8/cephfs.8*
%{_mandir}/man8/mount.ceph.8*
%{_mandir}/man8/radosgw.8*
%{_mandir}/man8/radosgw-admin.8*
%{_mandir}/man8/rados.8*
%{_mandir}/man8/rbd.8*
%{_mandir}/man8/ceph-authtool.8*
%{_mandir}/man8/ceph-debugpack.8*
%{_mandir}/man8/ceph-clsinfo.8*
%{_mandir}/man8/ceph-dencoder.8*
%{_mandir}/man8/ceph-rbdnamer.8*
%{python_sitelib}/rados.py*
%{python_sitelib}/rbd.py*
%dir %{_localstatedir}/lib/ceph/
%dir %{_localstatedir}/lib/ceph/tmp/
%dir %{_localstatedir}/log/ceph/

%files libs
%defattr(-,root,root,-)
%doc COPYING
%{_libdir}/librados.so.*
%{_libdir}/librbd.so.*
%{_libdir}/rados-classes/libcls_rbd.so.*
%{_libdir}/rados-classes/libcls_rgw.so*
%{_libdir}/rados-classes/libcls_lock*
%{_libdir}/rados-classes/libcls_kvs*
%{_libdir}/rados-classes/libcls_refcount*

%files libcephfs
%defattr(-,root,root,-)
%doc COPYING
%{_libdir}/libcephfs.so.*

%files fuse
%defattr(-,root,root,-)
%doc COPYING
%{_bindir}/ceph-fuse
%{_mandir}/man8/ceph-fuse.8*

%files devel
%defattr(-,root,root,-)
%doc COPYING
%{_includedir}/cephfs/libcephfs.h
#%{_includedir}/crush/crush.h
#%{_includedir}/crush/hash.h
#%{_includedir}/crush/mapper.h
#%{_includedir}/crush/types.h
%{_includedir}/rados/librados.h
%{_includedir}/rados/librados.hpp
%{_includedir}/rados/buffer.h
%{_includedir}/rados/page.h
%{_includedir}/rados/crc32c.h
#%{_includedir}/rados/librgw.h
%{_includedir}/rbd/librbd.h
%{_includedir}/rbd/librbd.hpp
%{_includedir}/rbd/features.h
%{_libdir}/libcephfs.so
%{_libdir}/librados.so
#%{_libdir}/librgw.so
%{_libdir}/librbd.so*
%{_libdir}/rados-classes/libcls_rbd.so
%{_mandir}/man8/librados-config.8*


%files radosgw
%defattr(-,root,root,-)
%{_bindir}/radosgw
%{_bindir}/radosgw-admin
%{_sysconfdir}/bash_completion.d/radosgw-admin

%changelog
* Thu Nov  1 2012 Josef Bacik <josef@toxicpanda.com> - 0.53-1
- Update to 0.53

* Mon Sep 24 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.51-3
- Fix automake 1.12 error

* Tue Sep 18 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.51-2
- Use system leveldb

* Fri Sep 07 2012 David Nalley <david@gnsa.us> - 0.51-1
- Updating to 0.51
- Updated url and source url. 

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.46-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed May  9 2012 Josef Bacik <josef@toxicpanda.com> - 0.46-1
- updated to upstream 0.46
- broke out libcephfs (rhbz# 812975)

* Mon Apr 23 2012 Dan Horák <dan[at]danny.cz> - 0.45-2
- fix detection of C++11 atomic header

* Thu Apr 12 2012 Josef Bacik <josef@toxicpanda.com> - 0.45-1
- updating to upstream 0.45

* Wed Apr  4 2012 Niels de Vos <devos@fedoraproject.org> - 0.44-5
- Add LDFLAGS=-lpthread on any ARM architecture
- Add CFLAGS=-DAO_USE_PTHREAD_DEFS on ARMv5tel

* Mon Mar 26 2012 Dan Horák <dan[at]danny.cz> 0.44-4
- gperftools not available also on ppc

* Mon Mar 26 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.44-3
- Remove unneeded patch

* Sun Mar 25 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.44-2
- Update to 0.44
- Fix build problems

* Mon Mar  5 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.43-1
- Update to 0.43
- Remove upstreamed compile fixes patch
- Remove obsoleted dump_pop patch

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.41-2
- Rebuilt for c++ ABI breakage

* Thu Feb 16 2012 Tom Callaway <spot@fedoraproject.org> 0.41-1
- update to 0.41
- fix issues preventing build
- rebuild against gperftools

* Sat Dec 03 2011 David Nalley <david@gnsa.us> 0.38-1
- updating to upstream 0.39

* Sat Nov 05 2011 David Nalley <david@gnsa.us> 0.37-1
- create /etc/ceph - bug 745462
- upgrading to 0.37, fixing 745460, 691033
- fixing various logrotate bugs 748930, 747101

* Fri Aug 19 2011 Dan Horák <dan[at]danny.cz> 0.31-4
- google-perftools not available also on s390(x)

* Mon Jul 25 2011 Karsten Hopp <karsten@redhat.com> 0.31-3
- build without tcmalloc on ppc64, BR google-perftools is not available there

* Tue Jul 12 2011 Josef Bacik <josef@toxicpanda.com> 0.31-2
- Remove curl/types.h include since we don't use it anymore

* Tue Jul 12 2011 Josef Bacik <josef@toxicpanda.com> 0.31-1
- Update to 0.31

* Tue Apr  5 2011 Josef Bacik <josef@toxicpanda.com> 0.26-2
- Add the compile fix patch

* Tue Apr  5 2011 Josef Bacik <josef@toxicpanda.com> 0.26
- Update to 0.26

* Tue Mar 22 2011 Josef Bacik <josef@toxicpanda.com> 0.25.1-1
- Update to 0.25.1

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.21.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Sep 29 2010 Steven Pritchard <steve@kspei.com> 0.21.3-1
- Update to 0.21.3.

* Mon Aug 30 2010 Steven Pritchard <steve@kspei.com> 0.21.2-1
- Update to 0.21.2.

* Thu Aug 26 2010 Steven Pritchard <steve@kspei.com> 0.21.1-1
- Update to 0.21.1.
- Sample configs moved to /usr/share/doc/ceph/.
- Added cclass, rbd, and cclsinfo.
- Dropped mkmonfs and rbdtool.
- mkcephfs moved to /sbin.
- Add libcls_rbd.so.

* Tue Jul  6 2010 Josef Bacik <josef@toxicpanda.com> 0.20.2-1
- update to 0.20.2

* Wed May  5 2010 Josef Bacik <josef@toxicpanda.com> 0.20-1
- update to 0.20
- disable hadoop building
- remove all the test binaries properly

* Fri Apr 30 2010 Sage Weil <sage@newdream.net> 0.19.1-5
- Remove java deps (no need to build hadoop by default)
- Include all required librados helpers
- Include fetch_config sample
- Include rbdtool
- Remove misc debugging, test binaries

* Thu Apr 30 2010 Josef Bacik <josef@toxicpanda.com> 0.19.1-4
- Add java-devel and java tricks to get hadoop to build

* Mon Apr 26 2010 Josef Bacik <josef@toxicpanda.com> 0.19.1-3
- Move the rados and cauthtool man pages into the base package

* Sun Apr 25 2010 Jonathan Dieter <jdieter@lesbg.com> 0.19.1-2
- Add missing libhadoopcephfs.so* to file list
- Add COPYING to all subpackages
- Fix ownership of /usr/lib[64]/ceph
- Enhance description of fuse client

* Tue Apr 20 2010 Josef Bacik <josef@toxicpanda.com> 0.19.1-1
- Update to 0.19.1

* Mon Feb  8 2010 Josef Bacik <josef@toxicpanda.com> 0.18-1
- Initial spec file creation, based on the template provided in the ceph src
