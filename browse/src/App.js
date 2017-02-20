import React from 'react';
import './App.css';
import axios from 'axios';

class Ad extends React.Component {
  render() {
    return (
      <li className="ad">
        <div className="twitter-account">
          {this.props.twitterAccount}
        </div>
        <div className="images">
          <img className="ad-screenshot" src={this.props.adScreenshotURL} alt="ad-screenshot" />
          <img className="page-screenshot" src={this.props.pageScreenshotURL} alt="page-screenshot" />
        </div>
      </li>
    )
  }
}

class App extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      ads: [],
      twitterAccountOnly: true
    }

    this.toggleTwitterAccountsOnly = this.toggleTwitterAccountsOnly.bind(this)
  }

  toggleTwitterAccountsOnly(e) {
    this.setState({ twitterAccountOnly: e.target.checked })
  }

  componentDidMount() {
    const jsonAdsPath = 'http://sleeping-giants.s3-website-us-east-1.amazonaws.com/out.json'
    axios.get(jsonAdsPath)
      .then(res => {
        const ads = res.data.ads
        this.setState({ ads: ads });
      });
  }

  render() {
    const baseURL = 'http://sleeping-giants.s3-website-us-east-1.amazonaws.com/'

    const filteredAds = this.state.twitterAccountOnly ?
      this.state.ads.filter((ad) => ad.Twitter_Account !== 'None' ) : this.state.ads;

    const Ads = filteredAds.map(function(ad, idx) {
      const adScreenshot = baseURL + ad.Ad_Screenshot
      const pageScreenshot = baseURL + ad.Page_Screenshot
      const twitterAccount = (ad.Twitter_Account || '').split('/')[0];
      const adURL = ad.URL

      return (
        <Ad key={idx}
          twitterAccount={twitterAccount}
          adScreenshotURL={adScreenshot}
          pageScreenshotURL={pageScreenshot}
          adURL={adURL}
          />
      )
    })

    return (
      <div className="App">
        <div className="App-header">
          <h2>Ad detector</h2>
        </div>
        <div>
          <form>
            Show Twitter Accounts Only &nbsp;
            <input type="checkbox"
              checked={this.state.twitterAccountOnly}
              onChange={this.toggleTwitterAccountsOnly}/>
          </form>
        </div>
        <div className="App-intro">
          <ul className="ads">
            {Ads}
          </ul>
        </div>
      </div>
    );
  }
}

export default App;
