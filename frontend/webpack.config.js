const resolve = require('path').resolve
const webpack = require('webpack')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const url = require('url')
const publicPath = ''
const CompressionWebpackPlugin = require('compression-webpack-plugin');
const { VueLoaderPlugin } = require('vue-loader')

module.exports = (options = {}) => ({
  entry: {
    vendor: './src/vendor',
    index: './src/main.js'
  },
  output: {
    path: resolve(__dirname, '../backend/' , 'dist'),
    filename: options.dev ? '[name].js' : '[name].js?[chunkhash]',
    chunkFilename: '[id].js?[chunkhash]',
    publicPath: options.dev ? '/assets/' : publicPath
  },
  module: {
    rules: [
      {
        test: /\.mjs$/i,
        resolve: { byDependency: { esm: { fullySpecified: false } } },
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader',
        options: {
          compilerOptions: {
            compatConfig: {
              MODE: 2
            }
          }
        }
      },
      {
        test: /\.js$/,
        use: ['babel-loader'],
        exclude: /node_modules/
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader']
      },
      {
        test: /\.(png|jpg|jpeg|gif|eot|ttf|woff|woff2|svg|svgz)(\?.+)?$/,
        use: [{
          loader: 'url-loader',
          options: {
            limit: 10000
          }
        }]
      }
    ]
  },
  optimization: {
    minimize: true,
    splitChunks: {
      minChunks: Infinity,
      chunks: 'all'
    }
  },
  plugins: [
    new VueLoaderPlugin(),
    new HtmlWebpackPlugin({
      template: 'src/index.html'
    }),
    new CompressionWebpackPlugin({
      filename: '[path].gz[query]',
      algorithm: 'gzip',
      test: /\.(js|css|html)$/,
      threshold: 10240,
      minRatio: 0.8
    })
  ],
  resolve: {
    alias: {
      '~': resolve(__dirname, 'src'),
      vue: '@vue/compat'
    },
    extensions: ['.ts', '.js', '.mjs', '.vue', '.json', '.css']
  },
  devServer: {
    host: '127.0.0.1',
    port: 8010,
    proxy: [
      {
        context: ['/api'],
        target: 'http://localhost:8080',
        pathRewrite: { '^/api': '' },
      },
    ],
    historyApiFallback: {
      index: url.parse(options.dev ? '/assets/' : publicPath).pathname
    }
  },
  externals: {
    'vue': 'Vue',
    'vue-router': 'VueRouter',
    'element-plus': 'ElementPlus'
  }
  // devtool: options.dev ? '#eval-source-map' : '#source-map'
})
