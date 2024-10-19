from persica.context.application import ApplicationContext
from persica.applicationbuilder import ApplicationBuilder

from src.utils.log import logs


def main():
    logs.info("App start")
    app = (
        ApplicationBuilder()
        .set_application_context_class(ApplicationContext)
        .set_scanner_packages(["src.core", "src.plugins"])
        .build()
    )
    app.run()


if __name__ == "__main__":
    main()
