#Module-Specific definitions
%define mod_name mod_auth_kerb
%define mod_conf 11_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Apache module to provides authentifation against a Kerberos server
Name:		apache-%{mod_name}
Version:	5.3
Release:	%mkrel 6
Group:		System/Servers
License:	BSD-like
URL:		http://modauthkerb.sourceforge.net/
Source0:	http://prdownloads.sourceforge.net/modauthkerb/%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}
Patch1:		mod_auth_kerb-5.0-gcc4.patch
Patch2:		mod_auth_kerb-5.0rc7-exports.diff
Requires:	krb5-libs
BuildRequires:	krb5-devel
BuildRequires:	automake1.7
BuildRequires:	autoconf2.5
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Mod_auth_kerb is an apache module designed to provide Kerberos
user authentication to the Apache web server. Using the Basic
Auth mechanism, it retrieves a username/password pair from the
browser and checks them against a Kerberos server as set up by
your particular organization. It also supports mutual ticket
authentication, but most browsers do not support that natively.

I might look into writing a netscape plugin for it at some point.
Some browsers also require being told that they are to use Basic
Auth as opposed to seeing KerberosV* and handling that as basic
auth. The module accounts for this and 'tricks' the browser into
thinking it's normal basic auth. 

If you are using the Basic Auth mechanmism, the module does not
do any special encryption of any sort. The passing of the
username and password is done with the same Base64 encoding that
Basic Auth uses. This can easily be converted to plain text. To
counter this, I would suggest also using mod_ssl. 

%prep

%setup -q -n %{mod_name}-%{version}
%patch1 -p1 -b .gcc4
%patch2 -p0 -b .exports

cp %{SOURCE1} %{mod_conf}

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
#export WANT_AUTOCONF_2_5=1
#libtoolize --copy --force; aclocal-1.7; autoconf

export APXS=%{_sbindir}/apxs

%configure2_5x --localstatedir=/var/lib \
    --with-krb5=%{_prefix} \
    --without-krb4

# this auto* magic is whacked!
#perl -pi -e "s|^KRB5_LDFLAGS.*|KRB5_LDFLAGS=-lgssapi_krb5 -lkrb5 -lk5crypto -lcom_err -lresolv|g" Makefile
#perl -pi -e "s|^KRB4_LDFLAGS.*|KRB4_LDFLAGS=-lkrb4 -ldes425 -lkrb5 -lk5crypto -lcom_err -lresolv|g" Makefile

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

rm -rf .libs; cp -rp src/.libs .

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc INSTALL LICENSE README
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
