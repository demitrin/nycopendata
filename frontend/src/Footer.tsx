function Footer() {
  return (
    <div className="footer">
      <div>
        <a
          href="https://2023.open-data.nyc/"
          target="_blank"
          rel="noopener noreferrer"
        >
          <img className="nycOpenData" src="/NYCOpenData_Logo.png"></img>
        </a>
      </div>
      <div>
        Created with curiosity{" "}
        <span>
          <a
            href="https://github.com/demitrin/nycopendata"
            target="_blank"
            rel="noopener noreferrer"
          >
            [github]
          </a>
        </span>
        <span>
          <a
            href="https://pudding.cool/projects/clocks/"
            target="_blank"
            rel="noopener noreferrer"
          >
            [prior art]
          </a>
        </span>
      </div>
    </div>
  );
}

export default Footer;
