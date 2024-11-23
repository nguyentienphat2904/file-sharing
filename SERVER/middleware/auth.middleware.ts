import { Request, Response, NextFunction } from "express";
import jwt, { JwtPayload } from "jsonwebtoken";
import bcrypt from 'bcryptjs';

import { PeerModel } from "../models/peer.models";

const authMiddleware = (req: Request, res: Response, next: NextFunction): void => {
    const authorizationHeader = req.headers['authorization'];
    const token = authorizationHeader?.split(' ')[1];
    if (!token) {
        res.status(401).json({
            message: "Invalid token"
        });
        return;
    }
    jwt.verify(token as string, process.env.JWT_ACCESS_SECRET as string, (err, decoded) => {
        if (err) {
            res.sendStatus(403);
            return;
        }
        next();
    });
}

// const checkRole = (allowedRoles: string[]) => {
//     return (req: Request, res: Response, next: NextFunction): void => {
//         const userRole = req.user?.role;
//         if (!allowedRoles.includes(userRole)) {
//             res.status(403).json({ message: "Access denied" });
//             return;
//         }
//         next();
//     };
// };

export { authMiddleware }