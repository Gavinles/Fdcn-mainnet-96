import React, { useState, useEffect } from 'react'; import CoPilot from './CoPilot';
export default function Dashboard({ account: initialAccount, setAccount: setGlobalAccount }) {
    const [account, setAccount] = useState(initialAccount);
    useEffect(() => { const i = setInterval(async () => { try { const r = await fetch(`/api/ledger/account/${account.id}`); if(r.ok) setAccount(d => ({...d, ...(await r.json())})); } catch(e){} }, 2000); return () => clearInterval(i); }, [account.id]);
    return (<div className="mainContainer"><header><div className="logo">FDCN</div><div className="accountInfo"><span><strong>{account.fex ? account.fex.toFixed(2) : 0}</strong> $FEX</span><span><strong>{account.su || 0}</strong> SU</span></div></header><CoPilot account={account}/></div>);
}
