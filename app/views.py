from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Member, Transaction
import requests
import json
from datetime import  date


def book_list(request):
    books = Book.objects.all()
    
    return render(request, 'books.html', {'books': books})

def dashboard(request):
    books = Book.objects.all()
    members = Member.objects.all()
    transact = Transaction.objects.all()
    debt = 0
    stock = 0
    issued = 0
    
    for t in transact:
        if t.return_date == None:
            issued += 1
    for m in members:
        debt += m.outstanding_debt
    for b in books:
        stock += b.stock_count
    
    return render(request, 'dashboard.html', {'books': books,'members': members,'debt':debt,'stock':stock,'issued':issued})


def issueBook(request, id):
    book = Book.objects.get(id=id)
    
    if request.method == 'POST':
        memberId = request.POST.get('memberId')
        rent = request.POST.get('rent')
        member = Member.objects.get(id=memberId)
        if (member.outstanding_debt+int(rent) > 500):
            print(True)
            return render(request,'issueBook.html',{'error':True,"member":member})
            
        transact = Transaction(book=book,member=member,rent_fee=rent)
        book.stock_count = book.stock_count - 1
        book.save()
        transact.save()
        return render(request,'issueBook.html',{'transact':True,"member":member})
    members = Member.objects.all()
    return render(request,'issueBook.html',{'members':members,'book':book})


def returnBook(request, id):
    book = Book.objects.get(id=id)
    
    if request.method == 'POST':
        memberId = request.POST.get('memberId')
        member = Member.objects.get(id=memberId)
        transact = Transaction.objects.filter(book=book,member=member)[0]
        member.outstanding_debt += transact.rent_fee
        book.stock_count += 1
        
        print(transact.return_date)
        transact.return_date = date.today()
        print(transact.return_date)
        member.save()
        transact.save()
        book.save()
        return render(request,'returnBook.html',{'transact':True,"member":member})
    

    transact = Transaction.objects.filter(book=book)
    members = []
    
    for t in transact:
        if t.return_date == None:
            print(True)
            members.append(t.member)
    
    return render(request,'returnBook.html',{'members': members,'book':book})
    
    
def members(request):
    members = Member.objects.all()
    books = []
    for member in members:
        transact = Transaction.objects.filter(member=member)
        books.append({"memberId":member.id, "books" : len(transact)})
    return render(request, 'members.html',{'members':members,'books':books})
    
    
def addMember(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        try:
            member = Member(name=name,email=email)
            member.save()
            return render(request,'addMember.html',{'created':True,'member':member})
        except:
            return render(request,'addMember.html',{'error':True,'member':member})
 
    return render(request,'addMember.html')

def deleteMember(request,id):
    member = Member.objects.get(id=id)
    member.delete()
    return redirect('/members')

def deleteBook(request,id):
    book = Book.objects.get(id=id)
    book.delete()
    return redirect('/')

def addBooks(request):
    
    if request.method == 'POST':
        title = request.POST.get('name')
        books = request.POST.get('books')
        quantity = request.POST.get('quantity')
        
        booksImported = 0
        page = 0
        while int(books)!=booksImported:
            page += 1
            res = requests.get(f'https://frappe.io/api/method/frappe-library?page={page}&title={title}').json()
            if (len(res['message'])>0):
                for book in res['message']:
                    if (int(books)==booksImported):
                        break
                    book = Book(
                        title=book['title'],
                        author=book['authors'],
                        isbn=book['isbn'],
                        publisher = book['publisher'],
                        page_count = book['  num_pages'],
                        stock_count = int(quantity)
                        
                    )
                    book.save()
                    booksImported += 1
            else:
                break
        return render(request,'addBooks.html',{'created':True,'books':booksImported})
    
    return render(request,'addBooks.html')


def search(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        books = Book.objects.all()
        searched = []
        for book in books:
            if (str(query).lower() in str(book.title).lower() or
                str(query).lower() in str(book.author).lower() or
                str(query).lower() in str(book.isbn).lower() or
                str(query).lower() in str(book.publisher).lower() or
                str(query).lower() in str(book.page_count).lower() 
                ):
                searched.append(book)
        return render(request,'search.html',{'books':searched})
    return redirect('/')
