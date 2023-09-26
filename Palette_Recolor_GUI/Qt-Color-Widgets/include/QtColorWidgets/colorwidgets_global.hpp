#ifndef QT_COLOR_WIDGETS_GLOBAL_H
#define QT_COLOR_WIDGETS_GLOBAL_H

#include <QtCore/QtGlobal>

#if defined(QTCOLORWIDGETS_STATICALLY_LINKED)
#    define QCP_EXPORT
#elif defined(QTCOLORWIDGETS_LIBRARY)
#    define QCP_EXPORT Q_DECL_EXPORT
#else
//#    define QCP_EXPORT Q_DECL_IMPORT
# define QCP_EXPORT 
#endif

#endif // QT_COLOR_WIDGETS_GLOBAL_H
