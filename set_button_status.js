let buttonStatus = { button: 1, status: 'OFF' };

export default function handler(req, res) {
    if (req.method === 'POST') {
        buttonStatus = req.body;
        res.status(200).json({ message: 'Status updated' });
    } else {
        res.status(405).json({ message: 'Method not allowed' });
    }
}
