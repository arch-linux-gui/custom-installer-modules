pkgname=alg-theme-cala-config
destname="/etc/calamares"
pkgver=24.04
pkgrel=1
pkgdesc="Custom modules for Arch Linux GUI"
arch=('any')
url="https://github.com/arch-linux-gui"
license=('GPL3')
makedepends=('git')
depends=()
conflicts=()
provides=("${pkgname}")
options=(!strip !emptydirs)
source=(${pkgname}::"git+${url}/${pkgname}#branch=main")
sha256sums=('SKIP')

package() {
	# Create the target directory
	install -dm755 "${pkgdir}${destname}"

	# Copy the files from the source to the /etc/calamares directory
	cp -r "${srcdir}/${pkgname}"/* "${pkgdir}${destname}"

	# Set the appropriate permissions for all files
	find "${pkgdir}${destname}" -type f -exec chmod 644 {} \;
	find "${pkgdir}${destname}" -type d -exec chmod 755 {} \;
}

