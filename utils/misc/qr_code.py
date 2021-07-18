import pyqrcode


def qr_link(link):
    qr = pyqrcode.create(link, 'L')
    qr.png('documents/qr_post_link.png', scale=6)
    file = open('documents/qr_post_link.png', 'rb')
    return file
