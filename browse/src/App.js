import React from 'react';
import './App.css';
import axios from 'axios';

class Ad extends React.Component {
  render() {
    const TwitterURL = this.props.twitterAccount !== 'None' ? <a href={'https://twitter.com/' + this.props.twitterAccount} target="_blank">@{this.props.twitterAccount}</a> : '';

    return (
      <tr className="ad">
        <td className="twitter-account">
          {TwitterURL}
        </td>
        <td>
          <img className="ad-screenshot" src={this.props.adScreenshotURL} alt="ad-screenshot" />
        </td>
        <td>
          <img className="page-screenshot" src={this.props.pageScreenshotURL} alt="page-screenshot" />
        </td>
      </tr>
    )
  }
}

class App extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      ads: [],
      twitterAccountOnly: false
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
          <table className="ads">
            <thead>
              <tr>
                <th>Twitter</th>
                <th>Ad Image</th>
                <th>Page Image</th>
              </tr>
            </thead>
            <tbody>
              {Ads}
            </tbody>
          </table>
        </div>
      </div>
    );
  }
}

export default App;
