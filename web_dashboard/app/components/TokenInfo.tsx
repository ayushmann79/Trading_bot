import TradeControls from "./TradeControls";

const TokenInfo = ({ token }) => {
  return (
    <div>
      <h2>{token.name} ({token.symbol})</h2>
      <TradeControls tokenId={token.id} chainId={token.chainId} />
    </div>
  );
};
