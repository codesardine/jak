# Author: Vitor Lopes <vmnlop@gmail.com>

pkgbase=('python-jade-application-kit')
pkgname=('python-jade-application-kit')
_module='Jade-Application-Kit'
pkgver='0.a23'
pkgrel=1
pkgdesc="Build desktop applications using web technologies on Linux, with Python, JavaScript, HTML5, and CSS3 and webkit."
url="https://codesardine.github.io/Jade-Application-Kit"
depends=('python' 'python-gobject')
makedepends=('python-setuptools')
license=('GPL')
arch=('any')
source=("https://files.pythonhosted.org/packages/source/j/jade-application-kit/Jade-Application-Kit-${pkgver}.tar.gz")
md5sums=('SKIP')

build() {
    cd "${srcdir}/${_module}-${pkgver}"
    python setup.py build
}

package() {
    depends+=()
    cd "${srcdir}/${_module}-${pkgver}"
    python setup.py install --root="${pkgdir}" --optimize=1 --skip-build
}
